# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)

A modular bioinformatics platform integrating structural biology, large-scale literature mining, and generative AI to analyse antibiotic resistance proteins from WHO priority pathogens.

## Architecture
## Modules

- **Module 1** ✓ — Structural pipeline (Nextflow + ESMFold + AlphaFold DB + fpocket + PostgreSQL)
- **Module 2** ✓ — LLM research assistant (PubMed RAG + ChromaDB + Llama 3.3 + Streamlit)
- **Module 3** ✓ — Interactive 3D visualisation + comparative druggability dashboard
## Application Pages

- **Home** — platform overview and protein summary table
- **Dashboard** — comparative druggability analysis with Plotly charts
- **3D Viewer** — interactive protein structures with binding pocket overlay
- **Research Assistant** — AI-powered literature search across 949 PubMed articles

## Key Results (WHO ESKAPE Pathogens)
| UniProt | Organism | Gene | Pockets | Best Druggability | Tier |
|---|---|---|---|---|---|
| Q9HYD3 | Pseudomonas aeruginosa | VIM-2 | 18 | 0.755 | 🟢 high |
| P25051 | Enterococcus faecium | VanA | 22 | 0.566 | 🟡 medium |
| Q9F663 | Klebsiella pneumoniae | KPC-2 | 17 | 0.427 | 🟡 medium |
| Q9KLB7 | Acinetobacter baumannii | OXA-23 | 25 | 0.180 | 🔴 low |
| B9A8S5 | Escherichia coli | NDM-1 | 34 | 0.168 | 🔴 low |

## Tech Stack
**Bioinformatics**
- Nextflow DSL2 — reproducible pipeline orchestration
- ESMFold (Meta) + AlphaFold DB — protein structure prediction
- fpocket — binding pocket detection and druggability scoring
- BioPython — sequence handling

**AI / ML**
- sentence-transformers (all-MiniLM-L6-v2) — semantic embeddings
- ChromaDB — vector database for literature search
- Llama 3.3 70B (Groq) — LLM for research synthesis
- RAG (Retrieval-Augmented Generation) — grounded AI responses

**Visualisation**
- 3Dmol.js — interactive 3D protein structure rendering
- Plotly — comparative analysis charts
- Streamlit — multi-page web application

**Infrastructure**
- PostgreSQL — structured results storage
- Docker — containerised workflows
- GitHub Actions CI — automated testing on every push

## Installation
```bash
git clone https://github.com/kagansaglam/resistai.git
cd resistai

curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

pip install requests psycopg2-binary chromadb sentence-transformers streamlit groq python-dotenv biopython plotly pandas

sudo apt install fpocket

cp .env.example .env
# Add your GROQ_API_KEY to .env
```

## Usage

```bash
# Run Module 1 — structural pipeline
nextflow run main.nf
nextflow run main.nf -resume

# Load results to PostgreSQL
python3 scripts/load_to_db.py data/pathogens.csv results/pockets/

# Run Module 2 — research assistant only
streamlit run module2/app.py
# Run full application (all modules)
streamlit run app/Home.py
```

## Environment Variables
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
## Literature Database

949 PubMed articles indexed across 33 queries covering:
- Carbapenem-resistant Enterobacteriaceae (CRE)
- MRSA / VRSA mechanisms
- Drug-resistant Mycobacterium tuberculosis
- ESBL and AmpC beta-lactamases
- Structural biology and drug discovery
- AI/ML applications in antimicrobial resistance

## Author

Kagan Saglam

## License

MIT
