#!/bin/bash
set -e

echo '🧬 ResistAI Setup'
echo '=================='

# 1. Check OS
if [[ '$OSTYPE' == 'linux-gnu'* ]]; then
    echo '[OK] Linux detected'
elif [[ '$OSTYPE' == 'darwin'* ]]; then
    echo '[OK] macOS detected'
else
    echo '[WARN] Unsupported OS — proceed with caution'
fi

# 2. Check Python
if ! command -v python3 &> /dev/null; then
    echo '[FAIL] Python3 not found. Please install Python 3.10+'
    exit 1
fi
echo '[OK] Python3 found'

# 3. Install Python dependencies
echo '[INFO] Installing Python dependencies...'
pip install requests psycopg2-binary chromadb sentence-transformers \
    streamlit groq python-dotenv biopython plotly pandas scipy matplotlib seaborn
echo '[OK] Python dependencies installed'

# 4. Install Nextflow
if ! command -v nextflow &> /dev/null; then
    echo '[INFO] Installing Nextflow...'
    curl -s https://get.nextflow.io | bash
    sudo mv nextflow /usr/local/bin/
    echo '[OK] Nextflow installed'
else
    echo '[OK] Nextflow already installed'
fi

# 5. Install fpocket
if ! command -v fpocket &> /dev/null; then
    echo '[INFO] Installing fpocket...'
    if command -v apt &> /dev/null; then
        sudo apt install -y fpocket 2>/dev/null || sudo snap install fpocket
    elif command -v brew &> /dev/null; then
        brew install fpocket
    else
        echo '[WARN] Could not install fpocket automatically'
        echo '       Please install manually: https://fpocket.sourceforge.net'
    fi
    echo '[OK] fpocket installed'
else
    echo '[OK] fpocket already installed'
fi

# 6. Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo '[INFO] .env file created from .env.example'
    echo '[ACTION] Please add your GROQ_API_KEY to .env'
else
    echo '[OK] .env already exists'
fi

# 7. Run pipeline
echo ''
echo '[INFO] Running ResistAI pipeline...'
nextflow run main.nf

# 8. Run statistical analysis
echo '[INFO] Running statistical analysis...'
python3 scripts/statistical_analysis.py
python3 scripts/plot_analysis.py

# 9. Export GFF3
echo '[INFO] Exporting GFF3 annotations...'
python3 scripts/export_gff3.py \
    results/sequences/ results/pockets/ results/resistai_annotations.gff3

# 10. Build vector database
echo '[INFO] Fetching PubMed literature...'
python3 module2/scripts/fetch_pubmed.py
echo '[INFO] Building ChromaDB vector database...'
python3 module2/scripts/build_vectordb.py

echo ''
echo '✅ ResistAI setup complete!'
echo ''
echo 'Run the application:'
echo '  streamlit run app/Home.py'