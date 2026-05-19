# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19697274.svg)](https://doi.org/10.5281/zenodo.19697274)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Nextflow](https://img.shields.io/badge/Nextflow-DSL2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Live platform:** [resistai.bio](https://resistai.bio)

---

## Problem

Antibiotic resistance kills ~700,000 people annually and is projected to cause 10 million deaths per year by 2050. Identifying which resistance proteins are druggable — and finding relevant literature fast — remains a critical bottleneck in antimicrobial drug discovery.

Existing tools are fragmented: structure prediction, pocket detection, and literature mining require separate workflows, different expertise, and significant manual effort.

## Solution

ResistAI automates the full pipeline in one platform:

1. **Fetches** resistance protein sequences from UniProt across WHO priority pathogens
2. **Predicts** 3D structures using AlphaFold DB v4
3. **Generates** protein embeddings using ESM-2 for similarity search and ML classification
4. **Detects** binding pockets and scores druggability using fpocket + XGBoost
5. **Mines** 2,508 PubMed articles using semantic search (RAG)
6. **Answers** research questions using Llama 3.3 70B grounded in literature
7. **Exposes** results via REST API and web platform for downstream integration

## Results

Applied to **2,433 AMR resistance proteins** across WHO priority pathogens:

| Metric | Value |
|---|---|
| Total proteins analysed | **2,433** |
| High druggability targets (score ≥ 0.7) | **1,198 proteins (49%)** |
| Medium druggability targets (0.4–0.7) | **717 proteins (29%)** |
| Best druggability score | **1.0** |
| PubMed articles indexed | **2,508** |

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ResistAI Pipeline                        │
└─────────────────────────────────────────────────────────────────┘

  MODULE 1 — Structural Analysis (Nextflow / Slurm / Docker)
  ──────────────────────────────────────────────────────────
  pathogens.csv
       │
       ▼
  FETCH_CARD ──── UniProt API ──── 2,433 protein sequences
       │
       ▼
  DOWNLOAD_STRUCTURES ──── AlphaFold DB v4 ──── PDB files
       │
       ▼
  FIND_POCKETS ──── fpocket ──── binding site geometry
       │
       ▼
  CLASSIFY ──── ESM-2 embeddings + XGBoost ──── druggability score
       │
       ▼
  SUMMARY_REPORT ──── PostgreSQL / Supabase

  MODULE 2 — Literature RAG
  ─────────────────────────
  PubMed API (2,508 articles)
       │
       ▼
  sentence-transformers ──── ChromaDB (vector store)
       │
       ▼
  RAG engine ──── Llama 3.3 70B (Groq)

  MODULE 3 — Web Platform
  ────────────────────────
  FastAPI (resistai-api.onrender.com)
       │
       ▼
  Next.js + Supabase ──── resistai.bio
       │
       ├── Protein search & druggability dashboard
       ├── ESM-2 similarity search
       ├── Literature RAG / AI assistant
       └── Email reports (Resend)
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| **Pipeline orchestration** | Nextflow DSL2, Slurm, Docker |
| **Structure & pockets** | AlphaFold DB v4, fpocket |
| **Embeddings & ML** | ESM-2, XGBoost |
| **Literature RAG** | sentence-transformers, ChromaDB, Groq (Llama 3.3 70B) |
| **API** | FastAPI |
| **Web frontend** | Next.js, Tailwind CSS, Supabase |
| **Email** | Resend |
| **Infrastructure** | Docker, Slurm/HPC, Vercel, Render |

---

## ESM-2 Embeddings

Protein sequences are embedded with **ESM-2** (650M parameter language model) to produce 1,280-dimensional representations. These embeddings are used for:

- **Similarity search** — find structurally/functionally related proteins via cosine similarity stored in ChromaDB
- **ML classification** — XGBoost druggability classifier trained on fpocket features augmented with ESM-2 embeddings
- **Clustering** — UMAP projection for visualising resistance family relationships

```bash
# Generate embeddings
python scripts/esm_embeddings.py --input data/proteins.fasta --output data/esm2_embeddings.npy

# Query similar proteins
GET /similar-proteins/{uniprot_id}
```

---

## API

```bash
# Get platform statistics
GET /stats

# List proteins (filter by tier, family)
GET /proteins?tier=high&limit=10

# Get protein details + binding pockets
GET /proteins/{uniprot_id}

# Semantic literature search
POST /search
{"query": "VIM-2 metallo-beta-lactamase inhibitor", "n_results": 10}

# AI research assistant
POST /ask
{"question": "Which KPC variants have the best druggability scores?"}

# Find similar proteins by ESM-2 embedding
GET /similar-proteins/{uniprot_id}
```

Full API docs: [resistai-api.onrender.com/docs](https://resistai-api.onrender.com/docs)

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
python3 scripts/esm_embeddings.py         # ESM-2 embeddings
python3 scripts/train_classifier.py       # XGBoost classifier
python3 scripts/statistical_analysis.py   # statistics
python3 scripts/plot_analysis.py          # figures
python3 module2/scripts/fetch_pubmed.py   # Module 2 literature
streamlit run app/Home.py                  # full app
```

---

## Related Repositories

| Repo | Description |
|---|---|
| [resistai-api](https://github.com/kagansaglam/resistai-api) | FastAPI backend — deployed at resistai-api.onrender.com |
| [resistai-web](https://github.com/kagansaglam/resistai-web) | Next.js web platform — deployed at resistai.bio |

---

## Author

Kagan Saglam

## License

MIT
