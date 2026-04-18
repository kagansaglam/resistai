import streamlit as st
import streamlit.components.v1 as components
import json
import os

st.set_page_config(page_title='ResistAI 3D Viewer', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI — 3D Protein Viewer')

PROTEINS = {
    'Q9HYD3': {'gene': 'VIM-2',  'organism': 'Pseudomonas aeruginosa',  'tier': 'high',   'score': 0.755, 'best_pocket': 5},
    'P25051': {'gene': 'VanA',   'organism': 'Enterococcus faecium',    'tier': 'medium', 'score': 0.566, 'best_pocket': 22},
    'Q9F663': {'gene': 'KPC-2',  'organism': 'Klebsiella pneumoniae',   'tier': 'medium', 'score': 0.427, 'best_pocket': 9},
    'Q9KLB7': {'gene': 'OXA-23', 'organism': 'Acinetobacter baumannii', 'tier': 'low',    'score': 0.180, 'best_pocket': 6},
    'B9A8S5': {'gene': 'NDM-1',  'organism': 'Escherichia coli',        'tier': 'low',    'score': 0.168, 'best_pocket': 7},
}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader('Select Protein')
    selected = st.selectbox('Protein', options=list(PROTEINS.keys()), format_func=lambda x: f"{PROTEINS[x]['gene']} ({x})")
    p = PROTEINS[selected]
    tier_color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}[p['tier']]
    st.markdown(f"**Gene:** {p['gene']}")
    st.markdown(f"**Organism:** {p['organism']}")
    st.markdown(f"**Druggability score:** {tier_color} {p['score']} ({p['tier']})")
    st.markdown(f"**Best pocket:** #{p['best_pocket']}")
    st.divider()
    style = st.selectbox('Protein style', ['cartoon', 'stick', 'sphere', 'surface'])
    color = st.selectbox('Color scheme', ['spectrum', 'chain', 'ssJmol'])
    show_pocket = st.checkbox('Show best druggable pocket', value=True)
    pocket_color = st.color_picker('Pocket color', '#FF4B4B')
pdb_path = f'results/structures/{selected}.pdb'
pdb_data = ''
if os.path.exists(pdb_path):
    with open(pdb_path) as f:
        pdb_data = f.read()

pocket_data = ''
if show_pocket:
    pocket_num = p['best_pocket']
    pocket_path = f'results/pockets_pdb/{selected}/pocket{pocket_num}_atm.pdb'
    if os.path.exists(pocket_path):
        with open(pocket_path) as f:
            pocket_data = f.read()

with col2:
    st.subheader(f"{p['gene']} — 3D Structure with Binding Pocket")
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
        st.info(f"🎯 Highlighted pocket #{p['best_pocket']} — druggability score: {p['score']} ({p['tier']} tier)")
    else:
        st.warning('Pocket PDB file not found.')