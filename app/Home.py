import streamlit as st

st.set_page_config(page_title='ResistAI', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI')
st.subheader('Antibiotic Resistance Research Platform')
st.caption('WHO ESKAPE Priority Pathogens | Structural Biology + GenAI')
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('### 📊 Dashboard')
    st.markdown('Comparative druggability analysis across all WHO priority resistance proteins.')
    st.page_link('pages/1_Dashboard.py', label='Open Dashboard', icon='📊')

with col2:
    st.markdown('### 🔬 3D Viewer')
    st.markdown('Interactive 3D protein structures with binding pocket visualisation.')
    st.page_link('pages/2_3D_Viewer.py', label='Open 3D Viewer', icon='🔬')

with col3:
    st.markdown('### 🤖 Research Assistant')
    st.markdown('AI-powered literature search across 949 PubMed articles.')
    st.page_link('pages/3_Research_Assistant.py', label='Open Assistant', icon='🤖')

st.divider()
st.markdown('''
| UniProt | Gene | Organism | Best Score | Tier |
|---|---|---|---|---|
| Q9HYD3 | VIM-2 | P. aeruginosa | 0.755 | 🟢 High |
| P25051 | VanA | E. faecium | 0.566 | 🟡 Medium |
| Q9F663 | KPC-2 | K. pneumoniae | 0.427 | 🟡 Medium |
| Q9KLB7 | OXA-23 | A. baumannii | 0.180 | 🔴 Low |
| B9A8S5 | NDM-1 | E. coli | 0.168 | 🔴 Low |
''')