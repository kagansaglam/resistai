import sys
import requests

uniprot_id = sys.argv[1]
fasta_file = sys.argv[2]
MAX_LEN    = 400

with open(fasta_file) as f:
    lines = f.readlines()
sequence = "".join(l.strip() for l in lines if not l.startswith(">"))
print(f"[INFO] {uniprot_id} — sequence length: {len(sequence)} aa")

if len(sequence) > MAX_LEN:
    af_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    r = requests.get(af_url, timeout=60)
    if r.status_code == 200:
        with open(f"{uniprot_id}.pdb", "w") as f:
            f.write(r.text)
        print(f"[OK] AlphaFold DB: {uniprot_id}.pdb saved")
        sys.exit(0)
    print(f"[INFO] Not in AlphaFold DB, truncating to {MAX_LEN} aa")
    sequence = sequence[:MAX_LEN]

url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
r = requests.post(url, data=sequence, timeout=300)
if r.status_code == 200:
    with open(f"{uniprot_id}.pdb", "w") as f:
        f.write(r.text)
    print(f"[OK] ESMFold: {uniprot_id}.pdb saved")
else:
    print(f"[FAIL] {uniprot_id} — {r.status_code}: {r.text[:200]}", file=sys.stderr)
    sys.exit(1)
