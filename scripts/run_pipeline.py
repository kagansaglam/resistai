"""
Pipeline: AlphaFold download + fpocket analysis for proteins in expanded_proteins.json.
Skips proteins that already have a pocket JSON in results/pockets/.
Run from: /home/kagan/resistai/
"""
import json
import os
import sys
import subprocess
import requests
import time
import shutil

POCKETS_DIR = os.path.abspath("results/pockets")
PROTEINS_JSON = "data/expanded_proteins.json"
FPOCKET = "/snap/bin/fpocket"
PYTHON = sys.executable

os.makedirs(POCKETS_DIR, exist_ok=True)

with open(PROTEINS_JSON) as f:
    proteins = json.load(f)

already_done = {
    fname.replace("_pockets.json", "")
    for fname in os.listdir(POCKETS_DIR)
    if fname.endswith("_pockets.json")
}

todo = [p for p in proteins if p["uniprot_id"] not in already_done]
print(f"[INFO] {len(proteins)} proteins total | {len(already_done)} done | {len(todo)} to process")

ok = skip = fail = 0

for i, prot in enumerate(todo, 1):
    uid = prot["uniprot_id"]
    pdb_path = os.path.join(POCKETS_DIR, f"{uid}.pdb")
    json_path = os.path.join(POCKETS_DIR, f"{uid}_pockets.json")

    # Download AlphaFold PDB — use API to get current model version URL
    try:
        api_resp = requests.get(
            f"https://alphafold.ebi.ac.uk/api/prediction/{uid}", timeout=15)
        if api_resp.status_code == 200 and api_resp.json():
            pdb_url = api_resp.json()[0].get("pdbUrl", "")
        else:
            pdb_url = ""
        if pdb_url:
            resp = requests.get(pdb_url, timeout=60)
            if resp.status_code == 200 and "ATOM" in resp.text:
                with open(pdb_path, "w") as f:
                    f.write(resp.text)
            else:
                with open(pdb_path, "w") as f:
                    f.write("PLACEHOLDER\n")
        else:
            with open(pdb_path, "w") as f:
                f.write("PLACEHOLDER\n")
    except Exception as e:
        print(f"[WARN] {uid} — download error: {e}")
        with open(pdb_path, "w") as f:
            f.write("PLACEHOLDER\n")
    time.sleep(0.3)

    # Run find_pockets.py from POCKETS_DIR so JSON lands there
    find_pockets = os.path.abspath("scripts/find_pockets.py")
    pdb_local = f"{uid}.pdb"
    result = subprocess.run(
        [PYTHON, find_pockets, uid, pdb_local],
        capture_output=True, text=True,
        cwd=POCKETS_DIR
    )
    if result.returncode != 0:
        print(f"[FAIL] {uid} — fpocket error: {result.stderr[:120]}")
        fail += 1
        # Write stub so we skip on re-run
        stub = {"uniprot_id": uid, "total_pockets": 0, "skipped": True,
                "summary": {"high_druggability": 0, "medium_druggability": 0,
                            "low_druggability": 0, "best_score": None, "best_pocket_id": None},
                "all_pockets": []}
        with open(json_path, "w") as f:
            json.dump(stub, f)
        continue

    line = result.stdout.strip().split("\n")[-1]
    if "[SKIP]" in line:
        skip += 1
    else:
        ok += 1
    print(f"[{i}/{len(todo)}] {line}")

    # Clean up fpocket output dir and PDB to save disk space
    out_dir = os.path.join(POCKETS_DIR, f"{uid}_out")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    if os.path.exists(pdb_path):
        os.remove(pdb_path)

print(f"\n[DONE] ok={ok} | skip={skip} | fail={fail}")
