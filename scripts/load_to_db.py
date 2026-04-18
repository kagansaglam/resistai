import json
import csv
import sys
import os
import psycopg2

DB_CONFIG = {
    "dbname":   "resistai",
    "user":     "resistai_user",
    "password": "resistai2026",
    "host":     "localhost",
    "port":     5432
}

pathogens_csv = sys.argv[1]
pockets_dir   = sys.argv[2]

conn = psycopg2.connect(**DB_CONFIG)
cur  = conn.cursor()

# Load proteins
with open(pathogens_csv) as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute("""
            INSERT INTO proteins (uniprot_id, organism, gene)
            VALUES (%s, %s, %s)
            ON CONFLICT (uniprot_id) DO NOTHING
        """, (row["uniprot_id"], row["organism"], row["gene"]))
        print(f"[OK] Protein inserted: {row['uniprot_id']}")

# Load pockets
for fname in os.listdir(pockets_dir):
    if not fname.endswith("_pockets.json"):
        continue

    fpath = os.path.join(pockets_dir, fname)
    with open(fpath) as f:
        d = json.load(f)

    uniprot_id = d["uniprot_id"]

    for p in d["all_pockets"]:
        cur.execute("""
            INSERT INTO pockets (
                uniprot_id, pocket_id, druggability_score,
                druggability_tier, volume_a3, hydrophobicity, polarity
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            uniprot_id,
            p.get("pocket_id"),
            p.get("druggability_score"),
            p.get("druggability_tier"),
            p.get("volume_A3"),
            p.get("hydrophobicity"),
            p.get("polarity")
        ))

    print(f"[OK] Pockets inserted: {uniprot_id} ({d['total_pockets']} pockets)")

conn.commit()
cur.close()
conn.close()

print("\n[OK] All data loaded to PostgreSQL")
