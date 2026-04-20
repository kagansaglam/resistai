import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title='ResistAI', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI')
st.subheader('Antibiotic Resistance Research Platform')
st.caption('144 WHO Priority Proteins | Structural Biology + GenAI | Nextflow DSL2')
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('### 📊 Dashboard')
    st.markdown('Comparative druggability analysis across 144 WHO priority resistance proteins. Interactive Plotly charts, tier distribution, top 20 ranking.')
    st.page_link('pages/1_Dashboard.py', label='Open Dashboard', icon='📊')

with col2:
    st.markdown('### 🔬 3D Viewer')
    st.markdown('Interactive 3D protein structures with binding pocket visualisation. Powered by 3Dmol.js. All 144 proteins available.')
    st.page_link('pages/2_3D_Viewer.py', label='Open 3D Viewer', icon='🔬')

with col3:
    st.markdown('### 🤖 Research Assistant')
    st.markdown('AI-powered literature search across 949 PubMed articles. Ask questions, get answers grounded in published research.')
    st.page_link('pages/3_Research_Assistant.py', label='Open Assistant', icon='🤖')

st.divider()

# Key metrics
if os.path.exists('results/proteins_annotated.csv'):
    df = pd.read_csv('results/proteins_annotated.csv')
    df = df[df['best_score'].notna()]
    high   = len(df[df['best_score'] >= 0.7])
    medium = len(df[(df['best_score'] >= 0.4) & (df['best_score'] < 0.7)])
    low    = len(df[df['best_score'] < 0.4])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Proteins', len(df))
    col2.metric('High Druggability', high)
    col3.metric('Medium Druggability', medium)
    col4.metric('Best Score', f'{df["best_score"].max():.3f}')
    st.divider()

# Protein table
st.subheader('Protein Summary')
if os.path.exists('results/proteins_annotated.csv'):
    df = pd.read_csv('results/proteins_annotated.csv')
    df = df[df['best_score'].notna()].sort_values('best_score', ascending=False)
    df['tier'] = df['best_score'].apply(lambda x: '🟢 High' if x >= 0.7 else '🟡 Medium' if x >= 0.4 else '🔴 Low')
    st.dataframe(df[['gene','organism','family','best_score','tier']].rename(columns={
        'gene': 'Gene', 'organism': 'Organism', 'family': 'Family',
        'best_score': 'Best Score', 'tier': 'Tier'
    }), use_container_width=True, hide_index=True)