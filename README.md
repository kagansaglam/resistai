# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19697274.svg)](https://doi.org/10.5281/zenodo.19697274)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Nextflow](https://img.shields.io/badge/Nextflow-DSL2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Problem

Antibiotic resistance kills ~700,000 people annually and is projected to cause 10 million deaths per year by 2050. Identifying which resistance proteins are druggable — and finding relevant literature fast — remains a critical bottleneck in antimicrobial drug discovery.

Existing tools are fragmented: structure prediction, pocket detection, and literature mining require separate workflows, different expertise, and significant manual effort.

## Solution

ResistAI automates the full pipeline in one platform:

1. **Fetches** resistance protein sequences from UniProt across WHO priority pathogens
2. **Predicts** 3D structures using ESMFold and AlphaFold DB
3. **Detects** binding pockets and scores druggability using fpocket
4. **Mines** 2,508 PubMed articles using semantic search (RAG)
5. **Answers** research questions using Llama 3.3 70B grounded in literature
6. **Exposes** results via REST API and CLI for downstream integration

## Results

Applied to **144 WHO priority resistance proteins** across 8 resistance families:

| Metric | Value |
|---|---|
| High druggability targets (score ≥ 0.7) | **48 proteins (33%)** |
| Best druggability score | **0.983** (InhA, M. tuberculosis) |
| ANOVA across resistance families | **F=7.099, p<0.0001** |
| TB resistance proteins mean score | **0.829** — highest family |
| Aminoglycoside enzymes mean score | **0.392** — lowest family |
| PubMed articles indexed | **2,508** |

Key finding: TB resistance proteins and efflux pumps are significantly more druggable than aminoglycoside-modifying enzymes — consistent with known drug discovery challenges in this class.

---

## Architecture

### Module 1 - Structural Pipeline
`pathogens.csv` -> `FETCH_CARD` (UniProt API) -> `RUN_ESMFOLD` (ESMFold + AlphaFold DB) -> `FIND_POCKETS` (fpocket) -> `SUMMARY_REPORT` -> PostgreSQL

### Module 2 - LLM Research Assistant
`PubMed API` (2,508 articles) -> `sentence-transformers` (embeddings) -> `ChromaDB` (vector DB) -> `RAG engine` -> `Llama 3.3 70B` (Groq) -> `Streamlit UI`

### Module 3 - Visualisation & Analysis
`proteins_annotated.csv` -> `Interactive Dashboard` (Plotly) + `3D Protein Viewer` (3Dmol.js) + `Research Assistant` (Streamlit) + `Statistical Analysis` (scipy)

### API & CLI
`FastAPI` REST endpoints + `predict.py` CLI -> github.com/kagansaglam/resistai-api

---

## API

```bash
# Get platform statistics
GET /stats

# List high-druggability proteins
GET /proteins?tier=high&limit=10

# Get protein details + binding pockets
GET /proteins/{uniprot_id}

# Search literature
POST /search
{"query": "VIM-2 metallo-beta-lactamase inhibitor", "n_results": 10}
```

Full API docs: https://github.com/kagansaglam/resistai-api

## CLI

```bash
python predict.py --stats
python predict.py --protein Q5U7L7
python predict.py --list --tier high --limit 10
python predict.py --search "carbapenem resistance KPC inhibitor"
```

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

## Quick Start

```bash
git clone https://github.com/kagansaglam/resistai.git
cd resistai
cp .env.example .env
# Add your GROQ_API_KEY to .env
bash setup.sh
streamlit run app/Home.py
```

## CLI & API

```bash
# Clone API repo
git clone https://github.com/kagansaglam/resistai-api.git
cd resistai-api
pip install -r requirements.txt
uvicorn main:app --port 8000

# Use CLI
python predict.py --stats
python predict.py --protein Q5U7L7
```

---

## Tech Stack

**Bioinformatics:** Nextflow DSL2 · ESMFold · AlphaFold DB · fpocket · BioPython · GFF3

**AI / ML:** RAG · ChromaDB · sentence-transformers · Llama 3.3 70B (Groq)

**API & CLI:** FastAPI · predict.py CLI · REST endpoints

**Web:** Next.js · Tailwind CSS · Supabase · Vercel · Streamlit · 3Dmol.js · Plotly

**Infrastructure:** PostgreSQL · Docker · GitHub Actions CI · HPC/SLURM · AWS EC2

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

```bash
bash setup.sh                              # full reproduction
nextflow run main.nf                       # Module 1
python3 scripts/statistical_analysis.py   # statistics
python3 scripts/plot_analysis.py          # figures
python3 module2/scripts/fetch_pubmed.py   # Module 2 literature
streamlit run app/Home.py                  # full app
```

---

## Author

Kagan Saglam

## License

MIT
