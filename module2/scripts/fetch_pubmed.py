import requests
import json
import time

QUERIES = [
    "KPC beta-lactamase carbapenem resistance Klebsiella",
    "NDM metallo-beta-lactamase carbapenem resistance",
    "OXA-23 OXA-48 carbapenem resistance Acinetobacter",
    "VIM IMP metallo-beta-lactamase Pseudomonas",
    "carbapenem-resistant Enterobacteriaceae CRE clinical",
    "VanA VanB vancomycin resistance Enterococcus VRE",
    "MRSA methicillin-resistant Staphylococcus aureus mechanism",
    "PBP2a mecA MRSA resistance mechanism",
    "KatG InhA isoniazid resistance Mycobacterium tuberculosis",
    "RpoB rifampicin resistance tuberculosis",
    "MDR-TB XDR-TB resistance mechanisms",
    "AmpC beta-lactamase Enterobacter resistance",
"ESBL extended-spectrum beta-lactamase clinical",
    "CTX-M beta-lactamase resistance E.coli",
    "fluoroquinolone resistance gyrA parC mutation",
    "colistin resistance mcr-1 Gram-negative",
    "Helicobacter pylori clarithromycin resistance",
    "Campylobacter fluoroquinolone resistance",
    "Salmonella multidrug resistance mechanisms",
    "Streptococcus pneumoniae penicillin resistance PBP",
    "Haemophilus influenzae ampicillin resistance",
    "Shigella antibiotic resistance mechanisms",
    "beta-lactamase inhibitor drug discovery structure",
    "antibiotic resistance protein structure drug target",
    "carbapenemase crystal structure binding site",
    "metallo-beta-lactamase zinc active site inhibitor",
    "AlphaFold protein structure antibiotic resistance",
    "machine learning antibiotic resistance prediction",
    "deep learning drug discovery antimicrobial",
    "antimicrobial resistance WHO global priority",
"ESKAPE pathogens clinical outcomes mortality",
    "nosocomial infection multidrug resistant bacteria",
    "antibiotic stewardship resistance prevention",
]

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query, max_results=30):
    r = requests.get(f"{BASE_URL}/esearch.fcgi", params={
        "db":      "pubmed",
        "term":    query,
        "retmax":  max_results,
        "retmode": "json",
        "sort":    "relevance"
    })
    ids = r.json()["esearchresult"]["idlist"]
    print(f"[INFO] '{query[:50]}' -> {len(ids)} articles")
    return ids
def fetch_article_details(pmids):
    r = requests.get(f"{BASE_URL}/esummary.fcgi", params={
        "db":      "pubmed",
        "id":      ",".join(pmids),
        "retmode": "json"
    })
    return r.json()


articles = []
seen_pmids = set()

for query in QUERIES:
    pmids = search_pubmed(query, max_results=30)
    if not pmids:
        continue
    new_pmids = [p for p in pmids if p not in seen_pmids]
    if not new_pmids:
        print("  [SKIP] All articles already fetched")
        continue
    details = fetch_article_details(new_pmids)
    for pmid in new_pmids:
        doc = details.get("result", {}).get(pmid, {})
        if not doc or pmid == "uids":
            continue
        seen_pmids.add(pmid)
        articles.append({
            "pmid":    pmid,
            "title":   doc.get("title", ""),
            "authors": [a.get("name", "") for a in doc.get("authors", [])],
            "journal": doc.get("source", ""),
            "year":    doc.get("pubdate", "")[:4],
            "query":   query
        })
    time.sleep(0.4)

print(f"\n[OK] Total unique articles: {len(articles)}")

with open("module2/data/pubmed_articles.json", "w") as f:
    json.dump(articles, f, indent=2)

print("[OK] Saved to module2/data/pubmed_articles.json")
