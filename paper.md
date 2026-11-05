---
title: 'ResistAI: An Integrated Computational Platform for Druggability Analysis of Antibiotic Resistance Proteins'
tags:
  - Python
  - Nextflow
  - antimicrobial resistance
  - drug discovery
  - protein structure
  - protein language models
authors:
  - name: Kagan Saglam
    orcid: 0009-0002-1274-7534
    affiliation: 1
affiliations:
  - name: University of Bologna, Italy
    index: 1
date: 1 November 2026
bibliography: paper.bib
---

# Summary

Antimicrobial resistance (AMR) is a leading global health threat, associated with an estimated 4.95 million deaths in 2019 [@murray2022]. Developing new antibiotics requires choosing, among many resistance-associated proteins, those that are plausible drug targets. `ResistAI` is an open-source platform that supports this choice. It retrieves resistance proteins from UniProt [@uniprot2023], obtains structures from the AlphaFold Protein Structure Database [@jumper2021; @varadi2022] or ESMFold [@lin2023], detects binding pockets and scores their druggability with fpocket [@leguilloux2009], embeds sequences with ESM-2 [@lin2023], and offers a retrieval-augmented literature assistant [@lewis2020]. Applied to 2,433 reviewed UniProt entries, it detected 63,937 pockets and placed 1,198 proteins (49.2%) in a high-druggability tier. The workflow runs as a Nextflow pipeline [@ditommaso2017] on a workstation or an HPC cluster, and as a web service that scores any UniProt entry on demand.

# Statement of need

Prioritising AMR targets involves several separate steps: finding candidate proteins, predicting or retrieving structures, detecting pockets, and reading the relevant literature. Each step has a good tool, but combining them requires scripting and expertise in several areas. `ResistAI` is aimed at computational biologists and medicinal chemists who want a ranked, reproducible list of resistance proteins with pocket-level evidence and literature context, without assembling the workflow themselves. A REST API and a web interface make the results available to users who do not run the pipeline.

# State of the field

Resources for AMR (for example databases of resistance determinants) catalogue which genes and proteins confer resistance. AlphaFold DB [@varadi2022] provides structures, and fpocket [@leguilloux2009] converts a structure into pocket descriptors and a druggability score. To my knowledge, no openly available tool combines these steps for resistance proteins together with embedding-based similarity search and a literature assistant. I therefore built an integrated workflow around existing, well-validated components and did not re-implement them.

# Software design

The pipeline has four stages implemented as Nextflow DSL2 modules: sequence retrieval, structure prediction, pocket detection, and a summary report. It supports local, Docker, SLURM and LSF execution. Structures come from AlphaFold DB when available and from the ESMFold API otherwise (sequences above 400 residues without an AlphaFold structure are truncated). The best pocket score per protein defines three tiers (high $\geq 0.7$, medium $0.4$ to $<0.7$, low $<0.4$). ESM-2 embeddings (480 dimensions) support cosine-similarity search, and an XGBoost classifier [@chen2016] predicts the tier from the embedding alone. On a held-out test set (487 proteins) it reached 64.9% accuracy and a weighted ROC-AUC of 0.791, against 49.3% for a majority-class baseline. The literature assistant indexes 2,508 PubMed abstracts with a sentence-transformer model [@reimers2019] in ChromaDB and passes the retrieved abstracts to Llama 3.3 70B [@grattafiori2024], which cites PubMed identifiers. A FastAPI service with fpocket in a Docker container scores any UniProt entry live, and a Next.js front end provides search, dashboards and case studies. The API and front end live in the separate `resistai-api` and `resistai-web` repositories.

The design has known limits. The druggability score is a geometric proxy computed on predicted structures and requires experimental validation. The classifier predicts the same proxy, so it shows how well embeddings approximate fpocket and not druggability itself. The train/test split is random and not homology-aware, so the reported performance is probably optimistic. Only 118 of the 2,433 proteins carry a curated family label, which limits family-level comparisons, and the literature assistant has not been benchmarked quantitatively.

# Research impact statement

The software, the full results table and the scripts that reproduce every number in the accompanying manuscript (`scripts/reproduce_paper_stats.py`, checked by the test suite in `tests/`) are public under the MIT licence and archived on Zenodo (10.5281/zenodo.19697274). A live platform (resistai.bio) and a documented REST API make the pre-computed scores and the on-demand analysis available without installation, and three worked case studies (InhA, VIM-7, KPC-2) show how the outputs can be read. The project is new and I do not yet have evidence of use by other groups.

# AI usage disclosure

Generative AI tools (Claude, Anthropic) were used to help draft this paper, to write the tests, the reproducibility script and parts of the documentation, and to recompute the reported statistics from the repository data. I reviewed all material and take responsibility for its content and accuracy.

# References
