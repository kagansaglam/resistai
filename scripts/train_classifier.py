"""
Train a druggability-tier classifier using ESM-2 embeddings.
Tiers: high (best_score >= 0.7), medium (>= 0.4), low (< 0.4)
Outputs: models/druggability_classifier.pkl
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

EMBEDDINGS_PATH = os.path.expanduser("~/resistai/data/embeddings.parquet")
ANNOTATED_CSV   = os.path.expanduser("~/resistai-api/data/proteins_annotated.csv")
MODEL_DIR       = os.path.expanduser("~/resistai/models")
MODEL_PATH      = os.path.join(MODEL_DIR, "druggability_classifier.pkl")
METRICS_PATH    = os.path.join(MODEL_DIR, "classifier_metrics.json")


def tier(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def main():
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

    log.info("Loading embeddings …")
    emb = pd.read_parquet(EMBEDDINGS_PATH)
    log.info(f"Embeddings shape: {emb.shape}")

    log.info("Loading annotations …")
    ann = pd.read_csv(ANNOTATED_CSV)[["uniprot_id", "best_score"]]
    ann["tier"] = ann["best_score"].apply(tier)

    merged = emb.merge(ann, on="uniprot_id", how="inner")
    log.info(f"Merged shape: {merged.shape}")
    log.info(f"Tier distribution:\n{merged['tier'].value_counts()}")

    feature_cols = [c for c in merged.columns if c.startswith("f")]
    X = merged[feature_cols].values.astype(np.float32)
    y = merged["tier"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    log.info(f"Train: {len(X_train)}  Test: {len(X_test)}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # XGBoost preferred; fall back to RandomForest
    if HAS_XGB:
        log.info("Training XGBoostClassifier …")
        clf = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
        )
    else:
        log.info("XGBoost not available — using RandomForestClassifier …")
        clf = RandomForestClassifier(n_estimators=300, max_depth=10,
                                     random_state=42, n_jobs=-1)

    cv_acc = cross_val_score(clf, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
    log.info(f"CV accuracy: {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)

    acc    = accuracy_score(y_test, y_pred)
    f1     = f1_score(y_test, y_pred, average="weighted")
    roc    = roc_auc_score(y_test, y_prob, multi_class="ovr", average="weighted")

    log.info(f"Test accuracy : {acc:.4f}")
    log.info(f"Test F1       : {f1:.4f}")
    log.info(f"Test ROC-AUC  : {roc:.4f}")
    log.info("\n" + classification_report(y_test, y_pred, target_names=le.classes_))

    metrics = {
        "model": type(clf).__name__,
        "n_train": int(len(X_train)),
        "n_test":  int(len(X_test)),
        "cv_accuracy_mean": float(cv_acc.mean()),
        "cv_accuracy_std":  float(cv_acc.std()),
        "test_accuracy": float(acc),
        "test_f1_weighted": float(f1),
        "test_roc_auc_ovr_weighted": float(roc),
        "classes": le.classes_.tolist(),
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    log.info(f"Metrics saved to {METRICS_PATH}")

    payload = {"model": clf, "label_encoder": le, "feature_cols": feature_cols}
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(payload, f)
    log.info(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
