# ResistAI

> **An end-to-end computational platform for antibiotic resistance research** — combining protein structure prediction, AI-powered literature mining, and interactive visualisation to identify druggable targets across 144 WHO priority resistance proteins.

[![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)](https://github.com/kagansaglam/resistai/actions)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Nextflow](https://img.shields.io/badge/Nextflow-DSL2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is ResistAI?

Antibiotic resistance is one of the most critical global health challenges — the WHO estimates it could cause 10 million deaths annually by 2050. Identifying druggable protein targets in resistant pathogens is a key step toward developing new treatments.

ResistAI automates this process end-to-end:

1. **Fetches** resistance protein sequences from UniProt across WHO priority pathogens
2. **Predicts** 3D structures using ESMFold and AlphaFold DB
3. **Detects** binding pockets and scores druggability using fpocket
4. **Mines** 949 PubMed articles using semantic search and RAG
5. **Answers** research questions using Llama 3.3 70B grounded in literature
6. **Visualises** everything in an interactive multi-page Streamlit application
---

## Architecture

### Module 1 - Structural Pipeline

`pathogens.csv` -> `FETCH_CARD` (UniProt API) -> `RUN_ESMFOLD` (ESMFold + AlphaFold DB) -> `FIND_POCKETS` (fpocket) -> `SUMMARY_REPORT` -> PostgreSQL

### Module 2 - LLM Research Assistant

`PubMed API` (949 articles) -> `sentence-transformers` (embeddings) -> `ChromaDB` (vector DB) -> `RAG engine` -> `Llama 3.3 70B` (Groq) -> `Streamlit UI`

### Module 3 - Visualisation & Analysis

`proteins_annotated.csv` -> `Interactive Dashboard` (Plotly) + `3D Protein Viewer` (3Dmol.js) + `Research Assistant` (Streamlit) + `Statistical Analysis` (scipy)

---

## Key Results

| Metric | Value |
|---|---|
| Total proteins analysed | 144 |
| High druggability (≥0.7) | 48 (33%) |
| Medium druggability (0.4–0.7) | 41 (28%) |
| Low druggability (<0.4) | 55 (38%) |
| Best druggability score | 0.983 |
| PubMed articles indexed | 949 |
| GFF3 annotation records | 2988 |
| ANOVA p-value (family comparison) | <0.0001 |

---
---

## Results & Figures

### Figure 1 — Druggability Analysis Overview
![Figure 1](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure1_druggability_analysis.png)

### Figure 2 — Top 20 Most Druggable Proteins
![Figure 2](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure2_top20_proteins.png)

### Figure 3 — Pocket Distribution Heatmap by Resistance Family
![Figure 3](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure3_heatmap.png)

### Figure 4 — Organism Distribution & Mean Druggability
![Figure 4](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure4_organisms.png)

---

## Modules

- **Module 1** — Structural pipeline (Nextflow DSL2 + ESMFold + AlphaFold DB + fpocket + PostgreSQL)
- **Module 2** — LLM research assistant (PubMed RAG + ChromaDB + Llama 3.3 70B + Streamlit)
- **Module 3** — Interactive 3D visualisation + comparative druggability dashboard

---

## Application Pages

| Page | Description |
|---|---|
| Home | Platform overview, protein summary table |
| Dashboard | Interactive druggability charts, top 20 proteins, tier distribution |
| 3D Viewer | Rotate/zoom protein structures, visualise binding pockets in colour |
| Research Assistant | Ask questions, get AI answers grounded in 949 PubMed articles |

---
## Quick Start

```bash
git clone https://github.com/kagansaglam/resistai.git
cd resistai
cp .env.example .env
# Add your API keys (see below)
bash setup.sh
streamlit run app/Home.py
```

---

## Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Then add your API keys:
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here   # optional
### How to get a GROQ_API_KEY (free)

1. Go to [console.groq.com](https://console.groq.com)
2. Click **Sign Up** — free account, no credit card required
3. Navigate to **API Keys** in the left sidebar
4. Click **Create API Key**
5. Copy the key and paste it into your `.env` file as `GROQ_API_KEY=...`

> Groq provides free access to Llama 3.3 70B — no usage limits for personal projects.

### How to get an ANTHROPIC_API_KEY (optional)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up and navigate to **API Keys**
3. Click **Create Key** and copy it
4. Paste into `.env` as `ANTHROPIC_API_KEY=...`

> The Anthropic key is optional — ResistAI uses Groq by default.

---

## Manual Installation

```bash
# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

# Install Python dependencies
pip install requests psycopg2-binary chromadb sentence-transformers \
    streamlit groq python-dotenv biopython plotly pandas scipy matplotlib seaborn

# Install fpocket
sudo apt install fpocket      # Ubuntu/Debian
brew install fpocket           # macOS
```

---

## Usage

```bash
# Module 1 — run structural pipeline
nextflow run main.nf
nextflow run main.nf -resume

# Module 1 — run with specific profile
nextflow run main.nf -profile docker
nextflow run main.nf -profile slurm

# Module 1 — load results to PostgreSQL
python3 scripts/load_to_db.py data/pathogens.csv results/pockets/

# Module 1 — export GFF3 annotations
python3 scripts/export_gff3.py results/sequences/ results/pockets/ results/resistai_annotations.gff3
# Module 2 — fetch literature and build vector database
python3 module2/scripts/fetch_pubmed.py
python3 module2/scripts/build_vectordb.py

# Statistical analysis and figures
python3 scripts/statistical_analysis.py
python3 scripts/plot_analysis.py

# Run full application (all modules)
streamlit run app/Home.py

# Run research assistant only
streamlit run module2/app.py
```

---

## Tech Stack

**Bioinformatics**
- Nextflow DSL2 — reproducible pipeline orchestration (local, Docker, SLURM, LSF)
- ESMFold (Meta) + AlphaFold DB — protein structure prediction
- fpocket — binding pocket detection and druggability scoring
- BioPython — sequence handling
- GFF3 — genomic annotation export with EMBL cross-references

**AI / ML**
- sentence-transformers — semantic embeddings (all-MiniLM-L6-v2)
- ChromaDB — persistent vector database
- Llama 3.3 70B (Groq) — LLM for research synthesis
- RAG — retrieval-augmented generation

**Statistical Analysis**
- One-way ANOVA (F=7.099, p<0.0001)
- Pairwise t-tests across resistance families
- scipy, pandas, matplotlib, seaborn

**Infrastructure**
- PostgreSQL — structured results storage
- Docker — containerised workflows
- GitHub Actions CI — automated testing

---

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

---

## Reproducibility

All results in this repository are fully reproducible:

```bash
# Full reproduction from scratch
bash setup.sh

# Individual steps
nextflow run main.nf                          # Module 1
python3 scripts/statistical_analysis.py       # Statistics
python3 scripts/plot_analysis.py              # Figures 1-4
python3 scripts/export_gff3.py ...           # GFF3
python3 module2/scripts/fetch_pubmed.py       # Module 2 literature
python3 module2/scripts/build_vectordb.py     # Module 2 vector DB
```

---

## Author

Kagan Saglam

## License

MIT
