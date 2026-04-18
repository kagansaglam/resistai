# ResistAI — Antibiotic Resistance Research Platform

![CI](https://github.com/kagansaglam/resistai/actions/workflows/ci.yml/badge.svg)

A modular bioinformatics pipeline integrating GenAI and structural biology tools
to analyse antibiotic resistance proteins from WHO priority pathogens.

## Pipeline Architecture
## Modules

- **Module 1** ✓ — Structural pipeline (Nextflow + ESMFold + fpocket + PostgreSQL)
- **Module 2** — LLM research assistant (RAG + PubMed + Claude API)
- **Module 3** — Interactive visualisation + academic output

## Results (WHO ESKAPE Pathogens)

| UniProt | Organism | Gene | Pockets | Best Score | Tier |
|---|---|---|---|---|---|
| Q9HYD3 | Pseudomonas aeruginosa | VIM-2 | 18 | 0.755 | high |
| P25051 | Enterococcus faecium | VanA | 22 | 0.566 | medium |
| Q9F663 | Klebsiella pneumoniae | KPC-2 | 17 | 0.427 | medium |
| Q9KLB7 | Acinetobacter baumannii | OXA-23 | 25 | 0.180 | low |
| B9A8S5 | Escherichia coli | NDM-1 | 34 | 0.168 | low |

## Requirements

- Nextflow >= 25.0
- Python >= 3.10
- Docker
- fpocket

## Installation

```bash
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
pip install requests psycopg2-binary
sudo apt install fpocket
```
## Usage

```bash
nextflow run main.nf
nextflow run main.nf -resume
```

## Author

Kagan Saglam
