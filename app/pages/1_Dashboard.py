import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title='ResistAI Dashboard', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI — Comparative Analysis Dashboard')
st.caption('WHO Priority Antibiotic Resistance Proteins — Druggability Analysis')

df = pd.read_csv('results/proteins_annotated.csv')
df = df[df['best_score'].notna()]

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Proteins', len(df))
col2.metric('High Druggability', len(df[df['best_score'] >= 0.7]))
col3.metric('Medium Druggability', len(df[(df['best_score'] >= 0.4) & (df['best_score'] < 0.7)]))
col4.metric('Best Score', f"{df['best_score'].max():.3f}")

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader('Mean Druggability by Resistance Family')
    family_stats = df.groupby('family')['best_score'].mean().sort_values(ascending=False)
    colors = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' for s in family_stats]
    fig = go.Figure(go.Bar(
        x=family_stats.index, y=family_stats.values,
        marker_color=colors,
        text=[f'{s:.3f}' for s in family_stats.values],
        textposition='outside'
    ))
    fig.update_layout(yaxis_title='Mean Druggability Score', yaxis_range=[0, 1.1],
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    fig.add_hline(y=0.7, line_dash='dash', line_color='#2ecc71')
    fig.add_hline(y=0.4, line_dash='dash', line_color='#f39c12')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Top 20 Most Druggable Proteins')
    top20 = df.nlargest(20, 'best_score')
    colors2 = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' for s in top20['best_score']]
    fig2 = go.Figure(go.Bar(
        x=top20['best_score'],
        y=[f"{r['gene']} ({r['uniprot_id']})" for _, r in top20.iterrows()],
        orientation='h', marker_color=colors2
    ))
    fig2.update_layout(yaxis={'categoryorder': 'total ascending'},
        xaxis_title='Best Druggability Score', xaxis_range=[0, 1.1],
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader('Score Distribution')
    fig3 = go.Figure(go.Histogram(
        x=df['best_score'], nbinsx=25,
        marker_color='#3498db', opacity=0.8
    ))
    fig3.add_vline(x=0.7, line_dash='dash', line_color='#2ecc71', annotation_text='High')
    fig3.add_vline(x=0.4, line_dash='dash', line_color='#f39c12', annotation_text='Medium')
    fig3.update_layout(xaxis_title='Best Druggability Score', yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader('Tier Distribution')
    high   = len(df[df['best_score'] >= 0.7])
    medium = len(df[(df['best_score'] >= 0.4) & (df['best_score'] < 0.7)])
    low    = len(df[df['best_score'] < 0.4])
    fig4 = go.Figure(go.Pie(
        labels=[f'High (n={high})', f'Medium (n={medium})', f'Low (n={low})'],
        values=[high, medium, low],
        marker_colors=['#2ecc71', '#f39c12', '#e74c3c']
    ))
    fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader('Full Protein Table')
search = st.text_input('Search by gene, organism or family')
filtered = df[df.apply(lambda r: search.lower() in str(r['gene']).lower() or
    search.lower() in str(r['organism']).lower() or
    search.lower() in str(r['family']).lower(), axis=1)] if search else df
st.dataframe(filtered[['gene','organism','family','total_pockets',
    'high_druggability','medium_druggability','low_druggability','best_score']].rename(columns={
    'gene': 'Gene', 'organism': 'Organism', 'family': 'Family',
    'total_pockets': 'Total Pockets', 'high_druggability': 'High',
    'medium_druggability': 'Medium', 'low_druggability': 'Low',
    'best_score': 'Best Score'
}), use_container_width=True, hide_index=True)