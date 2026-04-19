import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os

st.set_page_config(page_title='ResistAI 3D Viewer', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI — 3D Protein Viewer')

df = pd.read_csv('results/proteins_annotated.csv')
df = df[df['best_score'].notna()].sort_values('best_score', ascending=False)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader('Select Protein')
    options = {
        f"{row['gene']} ({row['uniprot_id']}) — {row['best_score']:.3f}": row['uniprot_id']
        for _, row in df.iterrows()
        if os.path.exists(f"results/structures/{row['uniprot_id']}.pdb")
    }
    selected_label = st.selectbox('Protein (sorted by druggability)', list(options.keys()))
    selected = options[selected_label]
    row = df[df['uniprot_id'] == selected].iloc[0]
    tier_color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
    if row['best_score'] >= 0.7:
        tier = 'high'
    elif row['best_score'] >= 0.4:
        tier = 'medium'
    else:
        tier = 'low'
    st.markdown(f"**Gene:** {row['gene']}")
    st.markdown(f"**Organism:** {row['organism']}")
    st.markdown(f"**Family:** {row['family']}")
    st.markdown(f"**Druggability:** {tier_color[tier]} {row['best_score']:.3f} ({tier})")
    st.markdown(f"**Total pockets:** {int(row['total_pockets'])}")
    st.divider()
    style = st.selectbox('Display style', ['cartoon', 'stick', 'sphere', 'surface'])
    color = st.selectbox('Color scheme', ['spectrum', 'chain', 'ssJmol'])
    show_pocket = st.checkbox('Show best druggable pocket', value=True)
    pocket_color = st.color_picker('Pocket color', '#FF4B4B')

pdb_path = f'results/structures/{selected}.pdb'
pdb_data = ''
if os.path.exists(pdb_path):
    with open(pdb_path) as f:
        content = f.read()
    if 'ATOM' in content:
        pdb_data = content

pocket_data = ''
if show_pocket:
    pocket_num = int(row['best_pocket_id']) if pd.notna(row['best_pocket_id']) else 1
    pocket_path = f'results/pockets_pdb/{selected}/pocket{pocket_num}_atm.pdb'
    if os.path.exists(pocket_path):
        with open(pocket_path) as f:
            pocket_data = f.read()

with col2:
    st.subheader(f"{row['gene']} — 3D Structure")
    if pdb_data:
        html = f'''
        <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.1.0/3Dmol-min.js"></script>
        <div id="viewer" style="width:100%;height:520px;background:#1a1a2e;border-radius:8px;"></div>
        <script>
        var viewer = $3Dmol.createViewer("viewer", {{backgroundColor:"#1a1a2e"}});
        var pdbData = `{pdb_data}`;
        viewer.addModel(pdbData, "pdb");
        viewer.setStyle({{}}, {{{style}: {{colorscheme: "{color}", opacity: 0.85}}}});
        var pocketData = `{pocket_data}`;
        if (pocketData.trim().length > 0) {{
            viewer.addModel(pocketData, "pdb");
            viewer.setStyle({{model: 1}}, {{sphere: {{color: "{pocket_color}", opacity: 0.7, radius: 1.2}}}});
        }}
        viewer.zoomTo();
        viewer.render();
        </script>
        '''
        components.html(html, height=540)
        if pocket_data:
            st.info(f"🎯 Pocket #{pocket_num} — druggability: {row['best_score']:.3f} ({tier})")
    else:
        st.warning('PDB structure not available for this protein.')