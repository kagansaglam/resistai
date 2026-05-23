"""
Generate ESM-2 embeddings for all proteins in proteins_annotated.csv.
Saves to ~/resistai/data/embeddings.parquet with resume support.
"""

import os
import time
import logging
import requests
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

ANNOTATED_CSV = os.path.expanduser("~/resistai-api/data/proteins_annotated.csv")
OUT_PARQUET   = os.path.expanduser("~/resistai/data/embeddings.parquet")
MODEL_NAME    = "facebook/esm2_t12_35M_UR50D"
BATCH_SIZE    = 8   # CPU-safe
MAX_SEQ_LEN   = 1022


def fetch_fasta(uniprot_id: str) -> str | None:
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                lines = r.text.strip().splitlines()
                return "".join(lines[1:])  # strip header
            if r.status_code == 404:
                return None
        except requests.RequestException as e:
            log.warning(f"{uniprot_id} attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    return None


def mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> np.ndarray:
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden_state * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return (summed / counts).cpu().numpy()


def main():
    Path(os.path.expanduser("~/resistai/data")).mkdir(parents=True, exist_ok=True)

    proteins = pd.read_csv(ANNOTATED_CSV)["uniprot_id"].tolist()
    log.info(f"Total proteins: {len(proteins)}")

    # Resume: load already-processed ids
    done_ids: set = set()
    if os.path.exists(OUT_PARQUET):
        existing = pd.read_parquet(OUT_PARQUET, columns=["uniprot_id"])
        done_ids = set(existing["uniprot_id"].tolist())
        log.info(f"Resuming — {len(done_ids)} already processed")

    todo = [p for p in proteins if p not in done_ids]
    log.info(f"Remaining: {len(todo)}")
    if not todo:
        log.info("Nothing to do.")
        return

    log.info(f"Loading model {MODEL_NAME} …")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model     = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    device = torch.device("cpu")
    model.to(device)
    log.info("Model loaded.")

    records = []
    skipped = []

    for i in range(0, len(todo), BATCH_SIZE):
        batch_ids = todo[i : i + BATCH_SIZE]
        seqs = {}
        for uid in batch_ids:
            seq = fetch_fasta(uid)
            if seq:
                seqs[uid] = seq[:MAX_SEQ_LEN]
            else:
                log.warning(f"No FASTA for {uid}, skipping")
                skipped.append(uid)

        if not seqs:
            continue

        ids_list = list(seqs.keys())
        seq_list = list(seqs.values())

        inputs = tokenizer(seq_list, return_tensors="pt", padding=True,
                           truncation=True, max_length=MAX_SEQ_LEN + 2)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        embeddings = mean_pool(outputs.last_hidden_state, inputs["attention_mask"])

        for uid, emb in zip(ids_list, embeddings):
            row = {"uniprot_id": uid}
            for j, val in enumerate(emb):
                row[f"f{j}"] = float(val)
            records.append(row)

        log.info(f"Processed {min(i + BATCH_SIZE, len(todo))}/{len(todo)}  ({len(skipped)} skipped)")

        # Checkpoint every 50 batches
        if len(records) > 0 and (i // BATCH_SIZE) % 50 == 49:
            _flush(records, done_ids, OUT_PARQUET)
            done_ids.update(r["uniprot_id"] for r in records)
            records = []

    if records:
        _flush(records, done_ids, OUT_PARQUET)

    log.info(f"Done. Skipped {len(skipped)} proteins: {skipped[:10]}")


def _flush(new_records: list, done_ids: set, out_path: str):
    new_df = pd.DataFrame(new_records)
    if os.path.exists(out_path):
        existing = pd.read_parquet(out_path)
        new_df = pd.concat([existing, new_df], ignore_index=True)
    new_df.to_parquet(out_path, index=False)
    log.info(f"Saved {len(new_df)} total rows to {out_path}")


if __name__ == "__main__":
    main()
