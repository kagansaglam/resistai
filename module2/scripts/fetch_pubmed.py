import requests
import json
import time

QUERIES = [
    # Carbapenem resistance
    "KPC beta-lactamase carbapenem resistance Klebsiella",
    "NDM metallo-beta-lactamase carbapenem resistance",
    "OXA-23 OXA-48 carbapenem resistance Acinetobacter",
    "VIM IMP metallo-beta-lactamase Pseudomonas",
    "carbapenem-resistant Enterobacteriaceae CRE clinical",
    "carbapenemase producing organisms epidemiology",
    "carbapenem resistance mechanisms review",
    # Glycopeptide resistance
    "VanA VanB vancomycin resistance Enterococcus VRE",
    "VanC VanD VanE glycopeptide resistance",
    "vancomycin intermediate resistant Staphylococcus VISA",
    "glycopeptide resistance mechanisms clinical",
    # MRSA
    "MRSA methicillin-resistant Staphylococcus aureus mechanism",
    "PBP2a mecA MRSA resistance mechanism",
    "community acquired MRSA epidemiology treatment",
    "MRSA biofilm virulence treatment",
    # TB resistance
    "KatG InhA isoniazid resistance Mycobacterium tuberculosis",
    "RpoB rifampicin resistance tuberculosis",
    "MDR-TB XDR-TB resistance mechanisms treatment",
    "tuberculosis drug resistance mutation review",
    "bedaquiline linezolid XDR-TB treatment",
    # Beta-lactamases
    "AmpC beta-lactamase Enterobacter resistance",
    "ESBL extended-spectrum beta-lactamase clinical",
    "CTX-M beta-lactamase resistance E.coli",
    "SHV TEM beta-lactamase plasmid resistance",
    "beta-lactamase inhibitor avibactam vaborbactam",
    "beta-lactamase structure active site inhibition",
    # Efflux pumps
    "efflux pump MexAB-OprM Pseudomonas resistance",
    "efflux pump AdeABC Acinetobacter resistance",
    "efflux pump AcrAB-TolC Escherichia resistance",
    "RND efflux pump structure inhibitor",
    "efflux pump inhibitor antimicrobial potentiation",
    # Aminoglycosides
    "aminoglycoside acetyltransferase resistance",
    "aminoglycoside phosphotransferase resistance",
    "aminoglycoside nucleotidyltransferase resistance",
    "aminoglycoside modifying enzyme structure",
    # Fluoroquinolones
    "fluoroquinolone resistance gyrA parC mutation",
    "plasmid mediated quinolone resistance qnr",
    "fluoroquinolone resistance clinical Enterobacteriaceae",
    # Colistin
    "colistin resistance mcr-1 plasmid",
    "polymyxin resistance LPS modification",
    "colistin last resort treatment Gram-negative",
    # Drug discovery
    "beta-lactamase inhibitor drug discovery structure",
    "antibiotic resistance protein structure drug target",
    "carbapenemase crystal structure binding site",
    "metallo-beta-lactamase zinc active site inhibitor",
    "AlphaFold protein structure antibiotic resistance",
    "machine learning antibiotic resistance prediction",
    "deep learning drug discovery antimicrobial",
    "virtual screening antibiotic resistance target",
    "fragment based drug discovery resistance protein",
    "antibiotic resistance druggability pocket detection",
    # Clinical / epidemiology
    "antimicrobial resistance WHO global priority 2024",
    "ESKAPE pathogens clinical outcomes mortality",
    "nosocomial infection multidrug resistant bacteria",
    "antibiotic stewardship resistance prevention",
    "antimicrobial resistance surveillance global",
    "One Health antimicrobial resistance environment",
    "antimicrobial resistance economic burden",
    # New antibiotics
    "novel antibiotic discovery natural product resistance",
    "phage therapy antibiotic resistant bacteria",
    "antimicrobial peptide resistance mechanism",
    "CRISPR antimicrobial resistance gene editing",
    "antibiotic combination therapy synergy resistance",
]

BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

def search_pubmed(query, max_results=40):
    for attempt in range(3):
        try:
            r = requests.get(f'{BASE_URL}/esearch.fcgi', params={
                'db': 'pubmed', 'term': query,
                'retmax': max_results, 'retmode': 'json', 'sort': 'relevance'
            }, timeout=30)
            data = r.json()
            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                return data['esearchresult']['idlist']
            time.sleep(5)
        except Exception as e:
            print(f'[WARN] Attempt {attempt+1}/3 failed: {e}')
            time.sleep(10)
    return []

def fetch_details(pmids):
    r = requests.get(f'{BASE_URL}/esummary.fcgi', params={
        'db': 'pubmed', 'id': ','.join(pmids), 'retmode': 'json'
    })
    return r.json()

# Load existing articles
import os
existing_path = 'module2/data/pubmed_articles.json'
if os.path.exists(existing_path):
    with open(existing_path) as f:
        articles = json.load(f)
    seen = {a['pmid'] for a in articles}
    print(f'[INFO] Loaded {len(articles)} existing articles')
else:
    articles = []
    seen = set()

for query in QUERIES:
    pmids = search_pubmed(query, max_results=40)
    new_pmids = [p for p in pmids if p not in seen]
    if not new_pmids:
        print(f'[SKIP] {query[:50]}')
        continue
    details = fetch_details(new_pmids)
    count = 0
    for pmid in new_pmids:
        doc = details.get('result', {}).get(pmid, {})
        if not doc or pmid == 'uids':
            continue
        seen.add(pmid)
        articles.append({
            'pmid':    pmid,
            'title':   doc.get('title', ''),
            'authors': [a.get('name','') for a in doc.get('authors', [])],
            'journal': doc.get('source', ''),
            'year':    doc.get('pubdate', '')[:4],
            'query':   query
        })
        count += 1
    print(f'[OK] {query[:50]} -> {count} new articles')
    time.sleep(0.4)

print(f'\n[OK] Total unique articles: {len(articles)}')
with open('module2/data/pubmed_articles.json', 'w') as f:
    json.dump(articles, f, indent=2)
print('[OK] Saved to module2/data/pubmed_articles.json')