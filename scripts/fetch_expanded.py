import requests
import json
import time
import re

BASE_URL = 'https://rest.uniprot.org/uniprotkb/search'
FIELDS = "accession,protein_name,organism_name,gene_names"

results = []
seen = set()

def parse_next(link_header):
    """Extract next-page URL from Link header."""
    m = re.search(r'<([^>]+)>;\s*rel="next"', link_header or '')
    return m.group(1) if m else None

def add_entry(entry, family):
    uid = entry['primaryAccession']
    if uid in seen:
        return False
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
    try:
        protein = entry['proteinDescription']['recommendedName']['fullName']['value']
    except (KeyError, TypeError):
        try:
            protein = entry['proteinDescription']['submissionNames'][0]['fullName']['value']
        except (KeyError, IndexError, TypeError):
            protein = 'unknown'
    if gene == 'unknown':
        gene = protein.split()[0][:15]
    results.append({
        'uniprot_id': uid,
        'gene':       gene,
        'organism':   entry['organism']['scientificName'],
        'protein':    protein,
        'family':     family
    })
    return True

def bulk_fetch(query, family, size=200):
    """Paginate through all results for a query."""
    url = BASE_URL
    params = {"query": query, "format": "json", "size": size, "fields": FIELDS}
    total_new = 0
    page = 0
    while True:
        try:
            r = requests.get(url, params=params if page == 0 else None,
                             timeout=30)
            r.raise_for_status()
        except Exception as e:
            print(f"  [WARN] {query[:60]} page {page}: {e}")
            break
        for entry in r.json().get('results', []):
            if add_entry(entry, family):
                total_new += 1
        next_url = parse_next(r.headers.get('Link', ''))
        if not next_url:
            break
        url = next_url
        params = None
        page += 1
        time.sleep(0.4)
    return total_new

def single_query(query, family, size=25):
    url = BASE_URL
    params = {"query": f"{query} AND reviewed:true", "format": "json",
              "size": size, "fields": FIELDS}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] '{query[:50]}': {e}")
        return 0
    n = sum(1 for e in r.json().get('results', []) if add_entry(e, family))
    time.sleep(0.4)
    return n

# ── Phase 1: Bulk keyword-based fetches (paginated) ──────────────────────────
print("=== Phase 1: Keyword bulk fetches ===")

KEYWORD_QUERIES = [
    # KW-0046 = Antibiotic resistance (covers most resistance proteins)
    ('keyword:KW-0046 AND reviewed:true', 'antibiotic resistance'),
    # Additional keywords not always tagged KW-0046
    ('keyword:"Vancomycin resistance" AND reviewed:true', 'glycopeptide resistance'),
    ('keyword:"Quinolone resistance" AND reviewed:true', 'fluoroquinolone resistance'),
    ('keyword:"Aminoglycoside resistance" AND reviewed:true', 'aminoglycoside resistance'),
    ('keyword:"Rifamycin resistance" AND reviewed:true', 'rifampicin resistance'),
]

for kq, fam in KEYWORD_QUERIES:
    n = bulk_fetch(kq, fam, size=200)
    print(f"[BULK] '{kq[:60]}' -> {n} new | total: {len(results)}")

# ── Phase 2: Targeted queries for mechanisms not in KW-0046 ──────────────────
print("\n=== Phase 2: Targeted mechanism queries ===")

TARGETED = [
    # --- TB-specific ---
    ("KatG isoniazid resistance Mycobacterium tuberculosis H37Rv", "TB resistance"),
    ("InhA enoyl-ACP reductase isoniazid tuberculosis", "TB resistance"),
    ("RpoB rifampicin resistance Mycobacterium tuberculosis", "TB resistance"),
    ("EmbB arabinosyltransferase ethambutol resistance tuberculosis", "TB resistance"),
    ("PncA pyrazinamidase pyrazinamide resistance tuberculosis", "TB resistance"),
    ("AtpE ATP synthase bedaquiline tuberculosis", "TB resistance"),
    ("Rv0678 mmpL5 clofazimine bedaquiline resistance tuberculosis", "TB resistance"),
    ("DprE1 DprE2 benzothiazinone resistance tuberculosis", "TB resistance"),
    ("MmpL3 mycolic acid transport tuberculosis", "TB resistance"),
    ("Eis aminoglycoside acetyltransferase kanamycin tuberculosis", "TB resistance"),
    ("TlyA rRNA methyltransferase capreomycin resistance tuberculosis", "TB resistance"),
    ("MshA mycothiol biosynthesis resistance tuberculosis", "TB resistance"),
    ("LdtMt1 LdtMt2 meropenem resistance tuberculosis", "TB resistance"),
    ("Rv2416c ethA monooxygenase ethionamide resistance tuberculosis", "TB resistance"),
    ("folP1 dihydropteroate synthase sulfonamide tuberculosis", "TB resistance"),
    ("thyA thymidylate synthase PAS resistance tuberculosis", "TB resistance"),
    ("PonA2 transpeptidase beta-lactam tuberculosis", "TB resistance"),
    ("Rv1258c TetV efflux resistance tuberculosis", "TB resistance"),
    # --- Oxazolidinone ---
    ("cfr 23S rRNA methyltransferase linezolid resistance", "oxazolidinone resistance"),
    ("OptrA phenicol oxazolidinone resistance ABC", "oxazolidinone resistance"),
    ("PoxtA phenicol oxazolidinone tetracycline resistance", "oxazolidinone resistance"),
    ("ribosomal protein L3 L4 linezolid resistance", "oxazolidinone resistance"),
    # --- Colistin/Polymyxin ---
    ("mcr-1 phosphoethanolamine lipid A colistin", "colistin resistance"),
    ("mcr-2 mcr-3 mcr-4 colistin resistance plasmid", "colistin resistance"),
    ("PmrA PmrB two-component polymyxin resistance", "colistin resistance"),
    ("MgrB colistin resistance sensor Klebsiella", "colistin resistance"),
    ("PhoP PhoQ regulatory polymyxin resistance", "colistin resistance"),
    ("ArnA ArnB lipid A aminoarabinose polymyxin resistance", "colistin resistance"),
    ("ArnC ArnD ArnT lipid A modification polymyxin", "colistin resistance"),
    ("LpxA LpxC lipid A biosynthesis resistance", "colistin resistance"),
    # --- Efflux (missed by keyword) ---
    ("MexA MexB OprM efflux RND Pseudomonas aeruginosa", "efflux pump"),
    ("MexC MexD OprJ efflux Pseudomonas", "efflux pump"),
    ("MexX MexY aminoglycoside efflux Pseudomonas", "efflux pump"),
    ("AdeA AdeB AdeC efflux Acinetobacter baumannii", "efflux pump"),
    ("AcrA AcrB TolC efflux Escherichia resistance", "efflux pump"),
    ("TolC outer membrane factor efflux resistance", "efflux pump"),
    ("OqxA OqxB efflux quinolone resistance", "efflux pump"),
    ("QepA efflux pump quinolone resistance", "efflux pump"),
    ("MdfA multidrug major facilitator Escherichia", "efflux pump"),
    ("EmrA EmrB EmrD major facilitator efflux", "efflux pump"),
    ("MacA MacB efflux azithromycin resistance", "efflux pump"),
    ("BcrA BcrB bacitracin ABC efflux resistance", "efflux pump"),
    ("VexB VexD VexH efflux Vibrio cholerae", "efflux pump"),
    ("CmeA CmeB CmeC efflux Campylobacter resistance", "efflux pump"),
    ("Bmr BmrR MFS efflux Bacillus subtilis", "efflux pump"),
    ("BmrA ABC efflux Bacillus subtilis resistance", "efflux pump"),
    ("MtrC MtrD MtrE efflux Neisseria gonorrhoeae", "efflux pump"),
    ("FarA FarB fatty acid efflux Neisseria", "efflux pump"),
    ("HefA HefB HefC efflux Helicobacter pylori", "efflux pump"),
    ("SmeB SmeE SmeF efflux Stenotrophomonas maltophilia", "efflux pump"),
    # --- Carbapenemases/beta-lactamases (specific) ---
    ("KPC serine carbapenemase resistance", "carbapenemase"),
    ("NDM-1 NDM-5 metallo-beta-lactamase zinc", "carbapenemase"),
    ("VIM-1 VIM-2 metallo-beta-lactamase", "carbapenemase"),
    ("IMP-1 IMP-4 IMP-8 metallo-beta-lactamase", "carbapenemase"),
    ("OXA-23 OXA-48 OXA-58 class D carbapenemase", "carbapenemase"),
    ("CMY-2 CMY-4 AmpC plasmid cephalosporinase", "beta-lactamase"),
    ("CTX-M-1 CTX-M-14 CTX-M-15 extended spectrum", "beta-lactamase"),
    ("TEM-1 TEM-3 TEM-52 penicillinase ESBL", "beta-lactamase"),
    ("SHV-1 SHV-5 SHV-12 SHV-18 beta-lactamase", "beta-lactamase"),
    ("PER-1 PER-2 ESBL beta-lactamase Pseudomonas", "beta-lactamase"),
    ("GES-1 GES-2 GES-5 extended spectrum carbapenemase", "beta-lactamase"),
    ("AmpC PDC class C beta-lactamase Pseudomonas", "beta-lactamase"),
    ("L1 L2 metallo serine beta-lactamase Stenotrophomonas", "beta-lactamase"),
    ("CphA metallo-beta-lactamase Aeromonas", "carbapenemase"),
    # --- PBP / Cell wall ---
    ("mecA PBP2a penicillin-binding protein MRSA", "beta-lactamase"),
    ("PBP2x PBP2b penicillin-binding Streptococcus pneumoniae", "beta-lactamase"),
    ("PBP3 penicillin-binding resistance Haemophilus", "beta-lactamase"),
    ("PASTA domain penicillin-binding protein kinase", "beta-lactamase"),
    ("D-Ala-D-Lac D-Ala-D-Ser vancomycin resistance ligase", "glycopeptide resistance"),
    ("VanH D-lactate dehydrogenase vancomycin resistance", "glycopeptide resistance"),
    ("VanX D,D-dipeptidase vancomycin resistance", "glycopeptide resistance"),
    ("VanY D-carboxypeptidase vancomycin resistance", "glycopeptide resistance"),
    ("VanZ teicoplanin resistance Enterococcus", "glycopeptide resistance"),
    ("VanW VanT vancomycin resistance Enterococcus", "glycopeptide resistance"),
    # --- Regulatory proteins ---
    ("MarA MarR multiple antibiotic resistance regulator", "other resistance"),
    ("RamA SoxS activator AcrAB efflux resistance", "other resistance"),
    ("BaeSR BaeSR two-component efflux resistance", "other resistance"),
    ("CpxR CpxA outer membrane stress resistance", "other resistance"),
    ("NalC NalD MexAB repressor Pseudomonas resistance", "other resistance"),
    ("MexT regulatory mexEF efflux Pseudomonas", "other resistance"),
    ("AcrR TetR repressor efflux resistance", "other resistance"),
    # --- Daptomycin ---
    ("MprF lysyl-phosphatidylglycerol daptomycin resistance", "other resistance"),
    ("GdpD glycerophosphodiester phosphodiesterase daptomycin resistance", "other resistance"),
    ("LiaF LiaS LiaR daptomycin resistance Enterococcus", "other resistance"),
    ("YycG YycH two-component daptomycin resistance", "other resistance"),
    # --- Fosfomycin ---
    ("FosA fosfomycin resistance Pseudomonas glutathione", "other resistance"),
    ("FosB fosfomycin thiol transferase Staphylococcus", "other resistance"),
    ("FosC fosfomycin kinase resistance Pseudomonas", "other resistance"),
    ("UhpT GlpT fosfomycin transport resistance", "other resistance"),
    # --- Fusidic acid ---
    ("FusB fusidic acid resistance Staphylococcus", "other resistance"),
    ("FusC fusidic acid resistance methyltransferase", "other resistance"),
    ("FusD fusidic acid resistance ribosome", "other resistance"),
    # --- Nitrofurantoin ---
    ("NfsA NfsB nitroreductase nitrofurantoin resistance", "other resistance"),
    # --- Metronidazole ---
    ("RdxA FrxA nitroreductase metronidazole resistance Helicobacter", "other resistance"),
    # --- Sulfonamide/Trimethoprim ---
    ("dfrA dfrB dihydrofolate reductase trimethoprim resistance", "other resistance"),
    ("FolP folP dihydropteroate synthase sulfonamide resistance", "other resistance"),
    # --- Macrolide/MLSB ---
    ("ErmA ErmB ErmC 23S rRNA methyltransferase macrolide", "other resistance"),
    ("ErmF ErmG ErmQ ErmX methyltransferase macrolide", "other resistance"),
    ("ErmSF ErmN macrolide methyltransferase Streptomyces", "other resistance"),
    ("MphA MphB macrolide phosphotransferase inactivation", "other resistance"),
    ("MsrA MsrB ABC transporter macrolide efflux", "other resistance"),
    ("MefA MefE macrolide efflux Streptococcus", "other resistance"),
    # --- Chloramphenicol ---
    ("CatB chloramphenicol acetyltransferase type B resistance", "other resistance"),
    ("FloR fexA chloramphenicol florfenicol resistance efflux", "other resistance"),
    ("Cml chloramphenicol resistance efflux MFS", "other resistance"),
    # --- Tetracycline ---
    ("TetA TetB TetC tetracycline efflux resistance MFS", "other resistance"),
    ("TetM TetO ribosomal protection tetracycline resistance", "other resistance"),
    ("TetX tetracycline inactivation FAD monooxygenase", "other resistance"),
    ("Tet(X4) tigecycline resistance flavoprotein", "other resistance"),
    # --- Streptomyces self-resistance (produces antibiotics, has resistance) ---
    ("aminoglycoside phosphotransferase self-resistance Streptomyces", "aminoglycoside resistance"),
    ("erythromycin resistance methyltransferase producer Saccharopolyspora", "other resistance"),
    ("chloramphenicol acetyltransferase Streptomyces resistance", "other resistance"),
    ("rifamycin resistance Amycolatopsis resistance", "rifampicin resistance"),
    ("lincosamide nucleotidyltransferase lnu resistance", "other resistance"),
    # --- Salmonella ---
    ("AcrB efflux pump Salmonella typhimurium multidrug", "efflux pump"),
    ("TolC outer membrane Salmonella efflux resistance", "efflux pump"),
    ("fluoroquinolone resistance GyrA ParC Salmonella", "fluoroquinolone resistance"),
    # --- Neisseria ---
    ("PBP2 penicillin-binding Neisseria gonorrhoeae resistance", "beta-lactamase"),
    ("GyrA ParC fluoroquinolone resistance Neisseria", "fluoroquinolone resistance"),
    ("beta-lactamase TEM-1 Neisseria gonorrhoeae", "beta-lactamase"),
    # --- Streptococcus pneumoniae ---
    ("PBP2x PBP2b PBP1A beta-lactam resistance Streptococcus", "beta-lactamase"),
    ("ErmB macrolide resistance methyltransferase Streptococcus", "other resistance"),
    ("MefA efflux macrolide Streptococcus pneumoniae", "efflux pump"),
    # --- Campylobacter ---
    ("CmeABC efflux resistance Campylobacter jejuni", "efflux pump"),
    ("tet(O) tetracycline resistance Campylobacter", "other resistance"),
    # --- Helicobacter ---
    ("clarithromycin resistance 23S rRNA methyltransferase Helicobacter", "other resistance"),
    ("metronidazole resistance rdxA Helicobacter pylori", "other resistance"),
    # --- Aeromonas ---
    ("carbapenemase CphA metallo-beta-lactamase Aeromonas hydrophila", "carbapenemase"),
    # --- Broader drug target modifications ---
    ("topoisomerase IV ParC ParE fluoroquinolone resistance gram-negative", "fluoroquinolone resistance"),
    ("DNA gyrase GyrA GyrB resistance Mycobacterium leprae", "fluoroquinolone resistance"),
    ("ribosome dimethyltransferase aminoglycoside resistance", "aminoglycoside resistance"),
    ("aminoglycoside nucleotidyltransferase ANT resistance gram-positive", "aminoglycoside resistance"),
    ("acetyltransferase bifunctional aminoglycoside resistance AAC APH", "aminoglycoside resistance"),
    # --- Additional efflux families ---
    ("PACE transporter antimicrobial efflux resistance", "efflux pump"),
    ("Resistance-nodulation-division RND efflux multidrug resistance", "efflux pump"),
    ("ABC-F ribosomal protection protein resistance", "other resistance"),
    ("VgaA VgaB VgaC ABC-F streptogramin resistance", "other resistance"),
    ("LsaA LsaB LsaC ABC-F lincosamine resistance", "other resistance"),
    ("OptrA ABC-F oxazolidinone phenicol resistance", "oxazolidinone resistance"),
]

for query, family in TARGETED:
    n = single_query(query, family, size=25)
    print(f"[OK] '{query[:55]}' -> {n} new | total: {len(results)}")

print(f'\n[DONE] Total unique reviewed proteins: {len(results)}')
with open('data/expanded_proteins.json', 'w') as f:
    json.dump(results, f, indent=2)
print('[OK] Saved to data/expanded_proteins.json')
