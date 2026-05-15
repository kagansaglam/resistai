import json
import csv
import sys
import os
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("json_files", nargs="*", help="pocket JSON files (default: results/pockets/*_pockets.json)")
parser.add_argument("--proteins", default="data/expanded_proteins.json", help="protein metadata JSON")
parser.add_argument("--output", default="summary_report.csv", help="output CSV path")
args = parser.parse_args()

json_files = args.json_files or glob.glob("results/pockets/*_pockets.json")

# Load protein metadata for join
metadata = {}
if os.path.exists(args.proteins):
    with open(args.proteins) as f:
        for p in json.load(f):
            metadata[p["uniprot_id"]] = p

rows = []
for fpath in json_files:
    with open(fpath) as f:
        d = json.load(f)
    if d.get("skipped"):
        continue
    s = d["summary"]
    if s["best_score"] is None:
        continue
    uid = d["uniprot_id"]
    meta = metadata.get(uid, {})
    rows.append({
        "uniprot_id":          uid,
        "total_pockets":       d["total_pockets"],
        "high_druggability":   s["high_druggability"],
        "medium_druggability": s["medium_druggability"],
        "low_druggability":    s["low_druggability"],
        "best_score":          s["best_score"],
        "best_pocket_id":      s["best_pocket_id"],
        "organism":            meta.get("organism", ""),
        "gene":                meta.get("gene", ""),
        "family":              meta.get("family", ""),
    })

rows.sort(key=lambda x: x["best_score"], reverse=True)

fieldnames = ["uniprot_id", "total_pockets", "high_druggability",
              "medium_druggability", "low_druggability", "best_score",
              "best_pocket_id", "organism", "gene", "family"]

os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
with open(args.output, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] Summary report: {len(rows)} proteins ranked by druggability -> {args.output}")
print()
print(f"  {'UniProt':<12} {'Total':>6} {'High':>5} {'Med':>5} {'Low':>5} {'Best Score':>11} {'Best Pocket':>12}  {'Organism':<35} {'Gene'}")
print(f"  {'-'*12} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*11} {'-'*12}  {'-'*35} {'-'*15}")
for r in rows[:20]:
    print(f"  {r['uniprot_id']:<12} {r['total_pockets']:>6} "
          f"{r['high_druggability']:>5} {r['medium_druggability']:>5} "
          f"{r['low_druggability']:>5} {r['best_score']:>11.3f} "
          f"{str(r['best_pocket_id']):>12}  {r['organism'][:35]:<35} {r['gene']}")
if len(rows) > 20:
    print(f"  ... and {len(rows)-20} more proteins")
