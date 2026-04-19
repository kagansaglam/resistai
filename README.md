# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)

A modular bioinformatics platform integrating structural biology, large-scale literature mining, and generative AI to analyse antibiotic resistance proteins from WHO priority pathogens.

## Architecture
Module 1: Structural Pipeline
pathogens.csv → FETCH_CARD → RUN_ESMFOLD → FIND_POCKETS → SUMMARY_REPORT → PostgreSQL
Module 2: LLM Research Assistant
PubMed (949 articles) → ChromaDB (vector DB) → RAG engine → Llama 3.3 → Streamlit UI
Module 3: Visualisation & Analysis
3D Protein Viewer (3Dmol.js) + Comparative Dashboard (Plotly) + Multi-page Streamlit App
## Key Results

| Metric | Value |
|---|---|
| Total proteins analysed | 144 |
| High druggability (≥0.7) | 48 |
| Medium druggability (0.4–0.7) | 41 |
| Low druggability (<0.4) | 55 |
| Best druggability score | 0.983 |
| PubMed articles indexed | 949 |
| GFF3 annotation records | 2988 |

## Results & Figures

### Figure 1 — Druggability Analysis Overview
![Figure 1](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure1_druggability_analysis.png)

### Figure 2 — Top 20 Most Druggable Proteins
![Figure 2](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure2_top20_proteins.png)

### Figure 3 — Pocket Distribution Heatmap by Resistance Family
![Figure 3](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure3_heatmap.png)

### Figure 4 — Organism Distribution & Mean Druggability
![Figure 4](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure4_organisms.png)

## Modules
- **Module 1** ✓ — Structural pipeline (Nextflow DSL2 + ESMFold + AlphaFold DB + fpocket + PostgreSQL)
- **Module 2** ✓ — LLM research assistant (PubMed RAG + ChromaDB + Llama 3.3 70B + Streamlit)
- **Module 3** ✓ — Interactive 3D visualisation + comparative druggability dashboard

## Application

The full multi-page Streamlit application includes:
- **Home** — platform overview and protein summary
- **Dashboard** — comparative druggability analysis with interactive Plotly charts
- **3D Viewer** — interactive protein structures with binding pocket overlay (3Dmol.js)
- **Research Assistant** — AI-powered literature search across 949 PubMed articles

## Tech Stack

**Bioinformatics**
- Nextflow DSL2 — reproducible pipeline orchestration (local, Docker, SLURM, LSF profiles)
- ESMFold (Meta) + AlphaFold DB — protein structure prediction
- fpocket — binding pocket detection and druggability scoring
- BioPython — sequence handling
- GFF3 — genomic annotation export with EMBL cross-references
**AI / ML**
- sentence-transformers (all-MiniLM-L6-v2) — semantic embeddings
- ChromaDB — vector database for literature search
- Llama 3.3 70B (Groq) — LLM for research synthesis
- RAG (Retrieval-Augmented Generation) — grounded AI responses

**Statistical Analysis**
- One-way ANOVA — druggability differences across resistance families (F=7.099, p<0.0001)
- Pairwise t-tests — family-level comparisons
- scipy, pandas, matplotlib, seaborn

**Visualisation**
- 3Dmol.js — interactive 3D protein structure rendering
- Plotly — comparative analysis charts
- Streamlit — multi-page web application

**Infrastructure**
- PostgreSQL — structured results storage
- Docker — containerised workflows
- GitHub Actions CI — automated testing on every push
## Quick Start

```bash
git clone https://github.com/kagansaglam/resistai.git
cd resistai
cp .env.example .env
# Add your GROQ_API_KEY to .env
bash setup.sh
streamlit run app/Home.py
```

## Manual Installation

```bash
# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

# Install Python dependencies
pip install requests psycopg2-binary chromadb sentence-transformers \
    streamlit groq python-dotenv biopython plotly pandas scipy matplotlib seaborn

# Install fpocket
sudo apt install fpocket   # Ubuntu/Debian
brew install fpocket        # macOS
```

## Usage

```bash
# Run structural pipeline (Module 1)
nextflow run main.nf
nextflow run main.nf -resume          # resume after failure

# Run with specific profile
nextflow run main.nf -profile docker
nextflow run main.nf -profile slurm

# Load results to PostgreSQL
python3 scripts/load_to_db.py data/pathogens.csv results/pockets/

# Statistical analysis and figures
python3 scripts/statistical_analysis.py
python3 scripts/plot_analysis.py

# Export GFF3 annotations
python3 scripts/export_gff3.py results/sequences/ results/pockets/ results/resistai_annotations.gff3

# Build literature database (Module 2)
python3 module2/scripts/fetch_pubmed.py
python3 module2/scripts/build_vectordb.py

# Run full application (all modules)
streamlit run app/Home.py

# Run research assistant only (Module 2)
streamlit run module2/app.py
```

## Environment Variables

```bash
cp .env.example .env
```
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # optional

## Statistical Results

One-way ANOVA across resistance families: **F=7.099, p<0.0001**

| Family | n | Mean Score | Std |
|---|---|---|---|
| TB resistance | 10 | 0.829 | 0.239 |
| Efflux pump | 9 | 0.769 | 0.212 |
| Cell wall | 5 | 0.661 | 0.195 |
| Other resistance | 19 | 0.654 | 0.261 |
| Beta-lactamase | 25 | 0.509 | 0.196 |
| Fluoroquinolone | 4 | 0.395 | 0.161 |
| Aminoglycoside | 20 | 0.392 | 0.152 |

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
