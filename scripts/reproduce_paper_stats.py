"""
Recompute the summary statistics reported in the ResistAI manuscript
from the full results table (results/proteins_annotated_full.csv).

Usage:
    python scripts/reproduce_paper_stats.py [path/to/proteins_annotated_full.csv]
"""

import sys
import json
from pathlib import Path

import pandas as pd
from scipy import stats

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "results" / "proteins_annotated_full.csv"
GENERIC_FAMILY = "antibiotic resistance"
MIN_FAMILY_SIZE = 5


def tier(score: float) -> str:
    """Druggability tier from the best-pocket fpocket score."""
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def compute_stats(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["tier"] = df["best_score"].map(tier)
    tiers = df["tier"].value_counts()

    labelled = df[df["family"] != GENERIC_FAMILY]
    groups = {f: g["best_score"] for f, g in labelled.groupby("family") if len(g) >= MIN_FAMILY_SIZE}
    anova = stats.f_oneway(*groups.values())

    family_table = (
        labelled[labelled["family"].isin(groups)]
        .groupby("family")["best_score"]
        .agg(["count", "mean", "std"])
        .sort_values("mean", ascending=False)
        .round(3)
    )

    return {
        "n_proteins": int(len(df)),
        "total_pockets": int(df["total_pockets"].sum()),
        "mean_score": round(float(df["best_score"].mean()), 3),
        "sd_score": round(float(df["best_score"].std()), 3),
        "tiers": {k: int(tiers.get(k, 0)) for k in ("high", "medium", "low")},
        "n_labelled_proteins": int(len(labelled)),
        "anova_F": round(float(anova.statistic), 3),
        "anova_p": float(anova.pvalue),
        "family_table": family_table.to_dict(orient="index"),
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    result = compute_stats(pd.read_csv(path))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
