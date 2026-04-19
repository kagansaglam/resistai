import sys
import subprocess
import os
import json

uniprot_id = sys.argv[1]
pdb_file   = sys.argv[2]

# Skip placeholder PDB files
with open(pdb_file) as f:
    content = f.read()
if 'PLACEHOLDER' in content or 'ATOM' not in content:
    print(f'[SKIP] {uniprot_id} — placeholder PDB, skipping pocket detection')
    output = {
        'uniprot_id':    uniprot_id,
        'total_pockets': 0,
        'skipped':       True,
        'summary': {
            'high_druggability':   0,
            'medium_druggability': 0,
            'low_druggability':    0,
            'best_score':          None,
            'best_pocket_id':      None
        },
        'all_pockets': []
    }
    with open(f'{uniprot_id}_pockets.json', 'w') as f:
        json.dump(output, f, indent=2)
    sys.exit(0)

result = subprocess.run(
    ['fpocket', '-f', pdb_file],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f'[FAIL] fpocket failed for {uniprot_id}', file=sys.stderr)
    print(result.stderr, file=sys.stderr)
    sys.exit(1)

base      = pdb_file.replace('.pdb', '')
out_dir   = f'{base}_out'
info_file = os.path.join(out_dir, f'{base}_info.txt')

pockets = []
current = {}
with open(info_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith('Pocket'):
            if current:
                pockets.append(current)
            current = {'pocket_id': line.split()[1]}
        elif ':' in line:
            key, val = line.split(':', 1)
            current[key.strip()] = val.strip()
if current:
    pockets.append(current)

def parse_float(val):
    try:
        return float(val)
    except:
        return None

enriched = []
for p in pockets:
    score  = parse_float(p.get('Druggability Score'))
    volume = parse_float(p.get('Volume'))
    hydro  = parse_float(p.get('Hydrophobicity score'))
    polar  = parse_float(p.get('Polarity score'))
    if score is not None:
        tier = 'high' if score >= 0.7 else 'medium' if score >= 0.4 else 'low'
    else:
        tier = 'unknown'
    enriched.append({
        'pocket_id':          p.get('pocket_id'),
        'druggability_score': score,
        'druggability_tier':  tier,
        'volume_A3':          volume,
        'hydrophobicity':     hydro,
        'polarity':           polar,
        'raw':                p
    })

enriched.sort(key=lambda x: x['druggability_score'] if x['druggability_score'] else -1, reverse=True)
high   = [p for p in enriched if p['druggability_tier'] == 'high']
medium = [p for p in enriched if p['druggability_tier'] == 'medium']
low    = [p for p in enriched if p['druggability_tier'] == 'low']

output = {
    'uniprot_id':     uniprot_id,
    'total_pockets':  len(enriched),
    'skipped':        False,
    'summary': {
        'high_druggability':   len(high),
        'medium_druggability': len(medium),
        'low_druggability':    len(low),
        'best_score':          enriched[0]['druggability_score'] if enriched else None,
        'best_pocket_id':      enriched[0]['pocket_id'] if enriched else None
    },
    'all_pockets': enriched
}

with open(f'{uniprot_id}_pockets.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f'[OK] {uniprot_id} — {len(enriched)} pockets | high: {len(high)} | medium: {len(medium)} | low: {len(low)}')