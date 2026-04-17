import sys
import requests

organism   = sys.argv[1]
gene       = sys.argv[2]
uniprot_id = sys.argv[3]

url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
r   = requests.get(url, timeout=30)

if r.status_code == 200:
    with open(f"{uniprot_id}.fasta", "w") as f:
        f.write(r.text)
    print(f"[OK] {organism} / {gene} ({uniprot_id})")
else:
    print(f"[FAIL] {uniprot_id} — HTTP {r.status_code}", file=sys.stderr)
    sys.exit(1)
