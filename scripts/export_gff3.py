import json
import csv
import os
import sys
import requests
import time
from datetime import date

sequences_dir = sys.argv[1]
pockets_dir   = sys.argv[2]
output_gff3   = sys.argv[3]

meta = {}
with open('data/pathogens.csv') as f:
    for row in csv.DictReader(f):
        meta[row['uniprot_id']] = {'gene': row['gene'], 'organism': row['organism']}

def get_seq_len(fasta_path):
    seq = ''
    with open(fasta_path) as f:
        for line in f:
            if not line.startswith('>'):
                seq += line.strip()
    return len(seq)

def get_genomic_coords(uid):
    url = f'https://rest.uniprot.org/uniprotkb/{uid}.json'
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    for ref in data.get('uniProtKBCrossReferences', []):
        if ref.get('database') == 'EMBL':
            for prop in ref.get('properties', []):
                if prop.get('key') == 'ProteinId':
                    return ref.get('id', None)
    return None

records = []

for uid, info in meta.items():
    fasta_path  = os.path.join(sequences_dir, f'{uid}.fasta')
    pocket_path = os.path.join(pockets_dir, f'{uid}_pockets.json')
    if not os.path.exists(fasta_path):
        continue
    seq_len = get_seq_len(fasta_path)
    if seq_len == 0:
        continue

    # Try to get EMBL cross-reference
    embl_id = get_genomic_coords(uid)
    source_db = f'ResistAI;UniProt:{uid}'
    if embl_id:
        source_db += f';EMBL:{embl_id}'
    time.sleep(0.3)

    # Gene record — amino acid coordinates (1-based)
    records.append({
        'seqid':      uid,
        'source':     'ResistAI',
        'type':       'gene',
        'start':      1,
        'end':        seq_len,
        'score':      '.',
        'strand':     '+',
        'phase':      '.',
        'attributes': f'ID={uid};Name={info["gene"]};organism={info["organism"]};db_xref={source_db};coordinate_type=amino_acid'
    })

    # CDS record
    records.append({
        'seqid':      uid,
        'source':     'ResistAI',
        'type':       'CDS',
        'start':      1,
        'end':        seq_len,
        'score':      '.',
        'strand':     '+',
        'phase':      0,
        'attributes': f'ID={uid}_CDS;Parent={uid};product=antibiotic_resistance_protein'
    })

    # Pocket records
    if os.path.exists(pocket_path):
        with open(pocket_path) as f:
            d = json.load(f)
        for pocket in d.get('all_pockets', []):
            pid   = pocket['pocket_id']
            score = pocket['druggability_score'] or 0
            tier  = pocket['druggability_tier']
            records.append({
                'seqid':      uid,
                'source':     'fpocket',
                'type':       'binding_site',
                'start':      1,
                'end':        seq_len,
                'score':      round(score, 3),
                'strand':     '+',
                'phase':      '.',
                'attributes': f'ID={uid}_pocket{pid};Parent={uid};druggability_score={score:.3f};druggability_tier={tier}'
            })

with open(output_gff3, 'w') as f:
    f.write('##gff-version 3\n')
    f.write(f'##date {date.today()}\n')
    f.write('##source ResistAI pipeline\n')
    f.write('##coordinate-system amino-acid-position\n')
    f.write('#\n')
    for r in records:
        f.write('\t'.join([
            str(r['seqid']), str(r['source']), str(r['type']),
            str(r['start']), str(r['end']), str(r['score']),
            str(r['strand']), str(r['phase']), str(r['attributes'])
        ]) + '\n')

print(f'[OK] GFF3 written: {output_gff3}')
print(f'[OK] Total records: {len(records)}')