import requests
import json
import time

queries = [
    "KPC beta-lactamase Klebsiella pneumoniae",
    "NDM metallo-beta-lactamase",
    "OXA carbapenemase Acinetobacter",
    "VIM metallo-beta-lactamase Pseudomonas",
    "IMP metallo-beta-lactamase",
    "VanA VanB glycopeptide resistance Enterococcus",
    "VanC VanD VanE glycopeptide resistance",
    "PBP2a mecA MRSA Staphylococcus",
    "aminoglycoside acetyltransferase resistance",
    "aminoglycoside phosphotransferase resistance",
    "aminoglycoside nucleotidyltransferase resistance",
    "efflux pump MexA MexB resistance Pseudomonas",
    "efflux pump AdeA AdeB Acinetobacter",
    "efflux pump AcrA AcrB Escherichia",
    "CTX-M extended spectrum beta-lactamase",
    "SHV TEM beta-lactamase resistance",
    "AmpC beta-lactamase Enterobacter",
    "KatG isoniazid resistance Mycobacterium",
    "InhA isoniazid resistance tuberculosis",
    "RpoB rifampicin resistance Mycobacterium",
    "colistin resistance mcr Enterobacteriaceae",
    "fluoroquinolone resistance GyrA ParC",
    "chloramphenicol acetyltransferase resistance",
    "tetracycline resistance TetA TetB efflux",
    "dihydropteroate synthase sulfonamide resistance"
]

results = []
seen = set()

for query in queries:
    url = 'https://rest.uniprot.org/uniprotkb/search'
    params = {
        "query":  f"{query} AND reviewed:true",
        "format": "json",
        "size":   15,
        "fields": "accession,protein_name,organism_name,gene_names"
    }
    r = requests.get(url, params=params)
    count = 0
    for entry in r.json().get('results', []):
        uid = entry['primaryAccession']
        if uid in seen:
            continue
        seen.add(uid)
        gene = 'unknown'
        if entry.get('genes'):
            for g in entry['genes']:
                if g.get('geneName'):
                    gene = g['geneName']['value']
                    break
                elif g.get('orfNames'):
                    gene = g['orfNames'][0]['value']
                    break
        protein = entry['proteinDescription']['recommendedName']['fullName']['value']
        if gene == 'unknown':
            gene = protein.split()[0][:15]
        results.append({
            'uniprot_id': uid,
            'gene':       gene,
            'organism':   entry['organism']['scientificName'],
            'protein':    protein
        })
        count += 1
    print(f"[OK] '{query[:45]}' -> {count} new proteins")
    time.sleep(0.5)

print(f'\n[OK] Total unique proteins: {len(results)}')
with open('data/expanded_proteins.json', 'w') as f:
    json.dump(results, f, indent=2)
print('[OK] Saved to data/expanded_proteins.json')