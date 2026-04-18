import streamlit as st
import json
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title='ResistAI Dashboard', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI — Comparative Analysis Dashboard')
st.caption('WHO ESKAPE Priority Pathogens — Druggability Analysis')

# Load all pocket JSONs
pockets_dir = 'results/pockets'
data = []
gene_map = {
    'Q9HYD3': ('VIM-2',  'P. aeruginosa'),
    'P25051': ('VanA',   'E. faecium'),
    'Q9F663': ('KPC-2',  'K. pneumoniae'),
    'Q9KLB7': ('OXA-23', 'A. baumannii'),
    'B9A8S5': ('NDM-1',  'E. coli'),
}

for fname in sorted(os.listdir(pockets_dir)):
    if not fname.endswith('_pockets.json'):
        continue
    with open(os.path.join(pockets_dir, fname)) as f:
        d = json.load(f)
    uid = d['uniprot_id']
    gene, org = gene_map.get(uid, (uid, 'Unknown'))
    s = d['summary']
    data.append({
        'uniprot_id': uid,
        'gene': gene,
        'organism': org,
        'total_pockets': d['total_pockets'],
        'high': s['high_druggability'],
        'medium': s['medium_druggability'],
        'low': s['low_druggability'],
        'best_score': s['best_score'],
    })

df = pd.DataFrame(data).sort_values('best_score', ascending=False)
# Top metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Proteins', len(df))
col2.metric('Total Pockets', int(df['total_pockets'].sum()))
col3.metric('High Druggability', int(df['high'].sum()))
col4.metric('Best Score', f"{df['best_score'].max():.3f}")

st.divider()

# Druggability bar chart
col1, col2 = st.columns(2)

with col1:
    st.subheader('Best Druggability Score by Protein')
    colors = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' for s in df['best_score']]
    fig = go.Figure(go.Bar(
        x=df['gene'], y=df['best_score'],
        marker_color=colors,
        text=[f"{s:.3f}" for s in df['best_score']],
        textposition='outside'
    ))
    fig.update_layout(
        yaxis_title='Druggability Score',
        yaxis_range=[0, 1],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        showlegend=False
    )
    fig.add_hline(y=0.7, line_dash='dash', line_color='#2ecc71', annotation_text='High threshold')
    fig.add_hline(y=0.4, line_dash='dash', line_color='#f39c12', annotation_text='Medium threshold')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Pocket Count Distribution')
    fig2 = go.Figure(go.Bar(
        x=df['gene'],
        y=df['high'],   name='High',   marker_color='#2ecc71'
    ))
    fig2.add_trace(go.Bar(x=df['gene'], y=df['medium'], name='Medium', marker_color='#f39c12'))
    fig2.add_trace(go.Bar(x=df['gene'], y=df['low'],    name='Low',    marker_color='#e74c3c'))
    fig2.update_layout(
        barmode='stack', yaxis_title='Number of Pockets',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader('Protein Summary Table')
st.dataframe(df[['gene','organism','total_pockets','high','medium','low','best_score']].rename(columns={
    'gene': 'Gene', 'organism': 'Organism', 'total_pockets': 'Total Pockets',
    'high': 'High', 'medium': 'Medium', 'low': 'Low', 'best_score': 'Best Score'
}), use_container_width=True, hide_index=True)