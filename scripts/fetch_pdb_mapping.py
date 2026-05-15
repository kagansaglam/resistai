import pandas as pd
import requests
import time
import json
import os

df = pd.read_csv('results/proteins_annotated.csv')
uids = df['uniprot_id'].tolist()
print(f'Total proteins: {len(uids)}')

mapping = {}
batch_size = 50

for i in range(0, len(uids), batch_size):
    batch = uids[i:i+batch_size]
    try:
        r = requests.get(
            'https://rest.uniprot.org/uniprotkb/search',
            params={'query': 'accession:(' + ' OR '.join(batch) + ')', 'fields': 'accession,xref_pdb', 'format': 'json', 'size': 50},
            timeout=30
        )
        for entry in r.json().get('results', []):
            uid = entry['primaryAccession']
            pdbs = [ref['id'] for ref in entry.get('uniProtKBCrossReferences', []) if ref.get('database') == 'PDB']
            if pdbs:
                mapping[uid] = pdbs[0]
    except Exception as e:
        print(f'Error batch {i}: {e}')
    time.sleep(0.5)
    print(f'Processed {min(i+batch_size, len(uids))}/{len(uids)}')

print(f'\n[OK] {len(mapping)} proteins have PDB IDs')
os.makedirs('data', exist_ok=True)
with open('data/uniprot_pdb_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)
print('[OK] Saved to data/uniprot_pdb_mapping.json')