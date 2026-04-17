# ResistAI — Antibiotic Resistance Research Platform

A modular bioinformatics pipeline integrating GenAI and structural biology tools
to analyse antibiotic resistance proteins from WHO priority pathogens.

## Overview

ResistAI automates the retrieval, structure prediction, and binding pocket
detection of resistance proteins, with a downstream LLM-powered research
assistant (Module 2).

## Pipeline Architecture
## Modules

- **Module 1** — Structural pipeline (Nextflow + ESMFold + fpocket)
- **Module 2** — LLM research assistant (RAG + PubMed + Claude API) — coming soon
- **Module 3** — Interactive visualisation + academic output — coming soon

## Target Proteins (WHO ESKAPE Pathogens)

| Organism | Gene | UniProt | Resistance |
|---|---|---|---|
| Klebsiella pneumoniae | KPC-2 | Q9F663 | Carbapenem |
| Escherichia coli | NDM-1 | B9A8S5 | Carbapenem |
| Acinetobacter baumannii | OXA-23 | Q9KLB7 | Carbapenem |
| Pseudomonas aeruginosa | VIM-2 | Q9HYD3 | Beta-lactam |
| Enterococcus faecium | VanA | P25051 | Vancomycin |

## Requirements

- Nextflow >= 25.0
- Python >= 3.10
- Docker
- fpocket

## Installation

```bash
# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/

# Install Python dependencies
pip install requests

# Install fpocket
sudo apt install fpocket
```

## Usage

```bash
# Run full pipeline
nextflow run main.nf

# Resume after failure
nextflow run main.nf -resume
```

## Results
## Author

Kagan Saglam

## License

MIT
