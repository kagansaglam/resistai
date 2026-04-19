import json
import csv
import sys

json_files = sys.argv[1:]
rows = []

for fpath in json_files:
    with open(fpath) as f:
        d = json.load(f)
    if d.get('skipped'):
        continue
    s = d['summary']
    if s['best_score'] is None:
        continue
    rows.append({
        'uniprot_id':          d['uniprot_id'],
        'total_pockets':       d['total_pockets'],
        'high_druggability':   s['high_druggability'],
        'medium_druggability': s['medium_druggability'],
        'low_druggability':    s['low_druggability'],
        'best_score':          s['best_score'],
        'best_pocket_id':      s['best_pocket_id']
    })

rows.sort(key=lambda x: x['best_score'], reverse=True)

fieldnames = ['uniprot_id','total_pockets','high_druggability',
              'medium_druggability','low_druggability','best_score','best_pocket_id']

with open('summary_report.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'[OK] Summary report: {len(rows)} proteins ranked by druggability')
print()
print(f"  {'UniProt':<12} {'Total':>6} {'High':>5} {'Med':>5} {'Low':>5} {'Best Score':>11} {'Best Pocket':>12}")
print(f"  {'-'*12} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*11} {'-'*12}")
for r in rows[:20]:
    print(f"  {r['uniprot_id']:<12} {r['total_pockets']:>6} "
          f"{r['high_druggability']:>5} {r['medium_druggability']:>5} "
          f"{r['low_druggability']:>5} {r['best_score']:>11.3f} "
          f"{str(r['best_pocket_id']):>12}")
if len(rows) > 20:
    print(f'  ... and {len(rows)-20} more proteins')