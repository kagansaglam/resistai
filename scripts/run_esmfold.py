import sys
import requests
import time

uniprot_id = sys.argv[1]
fasta_file = sys.argv[2]
MAX_LEN    = 400

with open(fasta_file) as f:
    lines_ = f.readlines()
sequence = ''.join(l.strip() for l in lines_ if not l.startswith('>'))
print(f'[INFO] {uniprot_id} — sequence length: {len(sequence)} aa')

# Step 1: Always try AlphaFold DB first
af_url = f'https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb'
r = requests.get(af_url, timeout=60)
if r.status_code == 200:
    with open(f'{uniprot_id}.pdb', 'w') as f:
        f.write(r.text)
    print(f'[OK] AlphaFold DB: {uniprot_id}.pdb saved')
    sys.exit(0)

# Step 2: Try ESMFold (truncate if needed)
if len(sequence) > MAX_LEN:
    print(f'[INFO] Truncating to {MAX_LEN} aa')
    sequence = sequence[:MAX_LEN]

url = 'https://api.esmatlas.com/foldSequence/v1/pdb/'
for attempt in range(1, 4):
    try:
        r = requests.post(url, data=sequence, timeout=120)
        if r.status_code == 200:
            with open(f'{uniprot_id}.pdb', 'w') as f:
                f.write(r.text)
            print(f'[OK] ESMFold: {uniprot_id}.pdb saved')
            sys.exit(0)
        print(f'[WARN] Attempt {attempt}/3 — HTTP {r.status_code}')
        time.sleep(15 * attempt)
    except Exception as e:
        print(f'[WARN] Attempt {attempt}/3 — {e}')
        time.sleep(15 * attempt)

# Step 3: Skip gracefully — create empty placeholder
print(f'[SKIP] {uniprot_id} — could not fold, creating placeholder')
with open(f'{uniprot_id}.pdb', 'w') as f:
    f.write(f'REMARK  PLACEHOLDER — folding failed for {uniprot_id}\n')
sys.exit(0)