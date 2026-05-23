# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19697274.svg)](https://doi.org/10.5281/zenodo.19697274)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Nextflow](https://img.shields.io/badge/Nextflow-DSL2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Live platform:** [resistai.bio](https://resistai.bio) · **API:** [resistai-api.onrender.com/docs](https://resistai-api.onrender.com/docs) · **Case study:** [resistai.bio/case-study/vim2](https://resistai.bio/case-study/vim2)

---

## Problem

Antibiotic resistance kills ~700,000 people annually and is projected to cause 10 million deaths per year by 2050. Identifying which resistance proteins are druggable — and finding relevant literature fast — remains a critical bottleneck in antimicrobial drug discovery.

Existing tools are fragmented: structure prediction, pocket detection, and literature mining require separate workflows, different expertise, and significant manual effort.

## Solution

ResistAI automates the full pipeline in one platform:

1. **Fetches** resistance protein sequences from UniProt across WHO ESKAPE priority pathogens + *M. tuberculosis*
2. **Predicts** 3D structures using AlphaFold DB v4 (ESMFold fallback)
3. **Generates** protein embeddings using ESM-2 (480-dim) for similarity search and ML classification
4. **Detects** binding pockets and scores druggability using fpocket
5. **Classifies** druggability tier using XGBoost trained on ESM-2 embeddings (ROC-AUC 0.79)
6. **Mines** 2,508 PubMed articles using semantic RAG search
7. **Answers** research questions using Llama 3.3 70B grounded in retrieved literature
8. **Exposes** results via REST API, web platform, and email reports

## Results

Applied to **2,433 AMR resistance proteins** across WHO priority pathogens:

| Metric | Value |
|---|---|
| Total proteins analysed | **2,433** |
| High druggability targets (score ≥ 0.7) | **1,198 (49%)** |
| Medium druggability targets (0.4–0.7) | **717 (29%)** |
| Best druggability score | **1.000** |
| PubMed articles indexed | **2,508** |
| ML classifier test accuracy | **0.647** |
| ML classifier ROC-AUC (OvR weighted) | **0.793** |
| ESM-2 similarity search coverage | **2,433 proteins** |

---

## ML Druggability Classifier

XGBoost classifier trained on ESM-2 embeddings (480-dim) to predict druggability tier (high/medium/low):

| Metric | Value |
|---|---|
| Model | XGBoost (n_estimators=300, max_depth=6) |
| Features | ESM-2 embeddings (esm2_t12_35M_UR50D) |
| Training set | 1,946 proteins |
| Test set | 487 proteins |
| CV accuracy (5-fold) | 0.647 ± 0.019 |
| Test accuracy | 0.647 |
| Test F1 (weighted) | 0.641 |
| **ROC-AUC (OvR weighted)** | **0.793** |

Per-class performance:

| Class | Precision | Recall | F1 |
|---|---|---|---|
| High | 0.74 | 0.80 | **0.77** |
| Medium | 0.48 | 0.43 | 0.46 |
| Low | 0.62 | 0.58 | 0.60 |

> Druggability scores are structural proxies computed by fpocket on AlphaFold-predicted structures (Le Guilloux et al. 2009). Thresholds: high ≥ 0.7, medium ≥ 0.4. Experimental validation required.

---

## Pipeline Architecture
┌─────────────────────────────────────────────────────────────────┐
│                        ResistAI Pipeline                        │
└─────────────────────────────────────────────────────────────────┘
MODULE 1 — Structural Analysis (Nextflow DSL2 / Slurm / Docker)
──────────────────────────────────────────────────────────────
pathogens.csv (2,433 WHO ESKAPE + TB proteins)
│
▼
FETCH_SEQUENCES ──── UniProt REST API
│
▼
DOWNLOAD_STRUCTURES ──── AlphaFold DB v4 → ESMFold (fallback)
│
▼
FIND_POCKETS ──── fpocket 4.0 ──── cavity geometry + druggability score
│
▼
ESM_EMBEDDINGS ──── esm2_t12_35M_UR50D ──── 480-dim vectors → ChromaDB
│
▼
CLASSIFY ──── XGBoost ──── druggability tier (ROC-AUC 0.793)
│
▼
SUMMARY_REPORT ──── proteins_annotated.csv + embeddings.parquet
MODULE 2 — Literature RAG
─────────────────────────
PubMed E-utilities API (2,508 articles)
│
▼
ChromaDB vector index ──── cosine similarity search
│
▼
Llama 3.3 70B (Groq) ──── PMID-cited research summaries
MODULE 3 — Production Platform
───────────────────────────────
FastAPI (Render) ← resistai-api.onrender.com
│
▼
Next.js + Supabase (Vercel) ← resistai.bio
│
├── Protein search & druggability dashboard
├── ESM-2 similarity search (ChromaDB cosine)
├── ML druggability prediction (/predict-druggability)
├── Literature RAG + AI assistant
└── Email reports (Resend, noreply@resistai.bio)
---

## Tech Stack

| Layer | Tools |
|---|---|
| **Pipeline orchestration** | Nextflow DSL2, Slurm, Docker, Singularity |
| **Structure & pockets** | AlphaFold DB v4, fpocket 4.0 |
| **Embeddings & ML** | ESM-2 (HuggingFace), XGBoost, scikit-learn |
| **Literature RAG** | ChromaDB, Groq (Llama 3.3 70B) |
| **API** | FastAPI, uvicorn |
| **Web frontend** | Next.js 14, Tailwind CSS, Supabase |
| **Email** | Resend (noreply@resistai.bio) |
| **Infrastructure** | Docker, Slurm/HPC, Vercel, Render |

---

## API Reference

```bash
# Platform statistics
GET /stats

# List proteins (filter by tier, family, limit)
GET /proteins?tier=high&limit=10

# Protein details + binding pockets
GET /proteins/{uniprot_id}

# Find similar proteins by ESM-2 cosine similarity
GET /similar-proteins/{uniprot_id}?n=10

# ML druggability prediction
POST /predict-druggability
{"uniprot_id": "Q840P9"}

# Semantic literature search
POST /search
{"query": "VIM-2 metallo-beta-lactamase inhibitor", "n_results": 10}

# AI research assistant (RAG + Llama 3.3)
POST /ask
{"query": "Is VIM-2 a good drug target?", "articles": [...]}

# On-demand protein analysis
POST /analyse
{"query": "P04637"}

# Email report
POST /send-report
{"to_email": "...", "user_name": "...", "query": "...", "answer": "...", "articles": [...]}
```

Full interactive docs: [resistai-api.onrender.com/docs](https://resistai-api.onrender.com/docs)

---

## Quick Start

```bash
git clone https://github.com/kagansaglam/resistai.git
cd resistai
pip install -r requirements.txt
# Add GROQ_API_KEY to .env
python scripts/fetch_expanded.py          # fetch proteins from UniProt
python scripts/run_pipeline.py            # AlphaFold + fpocket analysis
python scripts/esm_embeddings.py         # ESM-2 embeddings
python scripts/index_embeddings.py       # ChromaDB indexing
python scripts/train_classifier.py       # XGBoost classifier
python scripts/summary_report.py         # generate CSV
```

Or run the full Nextflow pipeline:

```bash
nextflow run main.nf
```

---

## Figures

### Figure 1 — Druggability Analysis Overview
![Figure 1](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure1_druggability_analysis.png)

### Figure 2 — Top 20 Most Druggable Proteins
![Figure 2](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure2_top20_proteins.png)

### Figure 3 — Pocket Distribution Heatmap by Resistance Family
![Figure 3](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure3_heatmap.png)

### Figure 4 — Organism Distribution & Mean Druggability
![Figure 4](https://raw.githubusercontent.com/kagansaglam/resistai/main/results/figure4_organisms.png)

---

## Statistical Analysis

One-way ANOVA across resistance families: **F=7.099, p<0.0001**

| Family | n | Mean Score | Std |
|---|---|---|---|
| TB resistance | 15 | 0.829 | 0.239 |
| Efflux pump | 23 | 0.769 | 0.212 |
| Carbapenemase | 4 | 0.721 | 0.181 |
| Cell wall | 5 | 0.661 | 0.195 |
| Beta-lactamase | 12 | 0.509 | 0.196 |
| Colistin resistance | 18 | 0.487 | 0.201 |
| Aminoglycoside resistance | 1 | 0.392 | 0.152 |

---

## Related Repositories

| Repo | Description |
|---|---|
| [resistai-api](https://github.com/kagansaglam/resistai-api) | FastAPI backend — resistai-api.onrender.com |
| [resistai-web](https://github.com/kagansaglam/resistai-web) | Next.js frontend — resistai.bio |

---

## Case Study

Full end-to-end analysis of **VIM-7 metallo-β-lactamase** (*Pseudomonas aeruginosa*):
- Druggability score: 0.747 (high tier)
- ESM-2 similarity: VIM-1 (0.993), VIM-2 (0.988), NDM-1 (0.982)
- ML prediction: high (94.2% confidence)

→ [resistai.bio/case-study/vim2](https://resistai.bio/case-study/vim2)

---

## Author

Kagan Saglam · [resistai.bio](https://resistai.bio)

## License

MIT
