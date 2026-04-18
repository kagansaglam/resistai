import json
import csv
import sys

json_files = sys.argv[1:]
rows = []

for fpath in json_files:
    with open(fpath) as f:
        d = json.load(f)

    s = d["summary"]
    rows.append({
        "uniprot_id":          d["uniprot_id"],
        "total_pockets":       d["total_pockets"],
        "high_druggability":   s["high_druggability"],
        "medium_druggability": s["medium_druggability"],
        "low_druggability":    s["low_druggability"],
        "best_score":          s["best_score"],
        "best_pocket_id":      s["best_pocket_id"]
    })

rows.sort(key=lambda x: x["best_score"] if x["best_score"] else 0, reverse=True)

fieldnames = [
    "uniprot_id", "total_pockets",
    "high_druggability", "medium_druggability", "low_druggability",
    "best_score", "best_pocket_id"
]

with open("summary_report.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] Summary report saved: {len(rows)} proteins ranked by druggability")
print()
print(f"  {'UniProt':<10} {'Total':>6} {'High':>5} {'Med':>5} {'Low':>5} {'Best Score':>11} {'Best Pocket':>12}")
print(f"  {'-'*10} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*11} {'-'*12}")
for r in rows:
    print(f"  {r['uniprot_id']:<10} {r['total_pockets']:>6} "
          f"{r['high_druggability']:>5} {r['medium_druggability']:>5} "
          f"{r['low_druggability']:>5} {r['best_score']:>11.3f} "
          f"{r['best_pocket_id']:>12}")
