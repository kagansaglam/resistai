import streamlit as st
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv('/home/kagan/resistai/.env')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

st.set_page_config(page_title='ResistAI Research Assistant', page_icon='🤖', layout='wide')
st.title('🤖 ResistAI — Research Assistant')
st.caption('Powered by 2508 PubMed articles + Llama 3.3 70B')

@st.cache_resource
def load_rag():
    model      = SentenceTransformer('all-MiniLM-L6-v2')
    client     = chromadb.PersistentClient(path='module2/data/chroma_db')
    collection = client.get_collection('pubmed_articles')
    return model, collection

model, collection = load_rag()

def search_literature(query, n_results=10):
    embedding = model.encode([query]).tolist()
    results   = collection.query(query_embeddings=embedding, n_results=n_results)
    articles  = []
    for i, doc in enumerate(results['documents'][0]):
        meta = results['metadatas'][0][i]
        articles.append({
            'title':   doc,
            'pmid':    meta['pmid'],
            'journal': meta['journal'],
            'year':    meta['year'],
            'score':   round(1 - results['distances'][0][i], 3)
        })
    return articles

def ask_llm(question, articles):
    context = '\n'.join([
        f"- [PMID:{a['pmid']}] ({a['year']}) {a['title']} ({a['journal']})"
        for a in articles
    ])
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': 'You are ResistAI, an expert research assistant specialising in antibiotic resistance mechanisms and drug discovery. Base your answers on the provided PubMed literature. Cite papers using PMID. Be scientifically precise.'},
            {'role': 'user', 'content': f'Question: {question}\n\nRelevant literature:\n{context}'}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

with st.sidebar:
    st.header('Search Mode')
    mode = st.radio('', ['General question', 'Protein-specific'])
    st.divider()
    n_results = st.slider('Articles to retrieve', 5, 20, 10)
    st.divider()
    st.markdown(f'**Database:** 2508 PubMed articles')
    st.markdown('**Model:** Llama 3.3 70B (Groq)')

# Check if protein was selected from Dashboard
if 'selected_gene' in st.session_state:
    st.info(f"🔗 Redirected from Dashboard: **{st.session_state['selected_gene']}** ({st.session_state['selected_uniprot']})")
    mode = 'Protein-specific'

if mode == 'Protein-specific':
    st.subheader('Protein-specific Literature Search')
    if os.path.exists('results/proteins_annotated.csv'):
        df = pd.read_csv('results/proteins_annotated.csv')
        df = df[df['best_score'].notna()].sort_values('best_score', ascending=False)
        options = {f"{r['gene']} ({r['uniprot_id']}) — score: {r['best_score']:.3f}": r for _, r in df.iterrows()}
        # Pre-select protein from Dashboard if available
        default_idx = 0
        if 'selected_uniprot' in st.session_state:
            keys = list(options.keys())
            for i, k in enumerate(keys):
                if st.session_state['selected_uniprot'] in k:
                    default_idx = i
                    break
        selected_label = st.selectbox('Select protein', list(options.keys()), index=default_idx)
        row = options[selected_label]
        st.markdown(f"**Gene:** {row['gene']} | **Organism:** {row['organism']} | **Family:** {row['family']}")
        auto_query = f"{row['gene']} {row['organism']} antibiotic resistance mechanism drug target druggability"
        st.info(f'Auto query: {auto_query}')
        custom_q = st.text_input('Refine question (optional)')
        final_q  = custom_q if custom_q else auto_query
        if st.button('Search Literature', type='primary'):
            with st.spinner('Searching and generating answer...'):
                articles = search_literature(final_q, n_results=n_results)
                answer   = ask_llm(final_q, articles)
            st.subheader('Answer')
            st.markdown(answer)
            st.subheader(f'Retrieved Literature ({len(articles)} articles)')
            for a in articles:
                with st.expander(f"[{a['score']}] {a['title'][:80]}..."):
                    st.markdown(f"**PMID:** [{a['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{a['pmid']})")
                    st.markdown(f"**Journal:** {a['journal']} | **Year:** {a['year']}")
else:
    st.subheader('Ask a research question')
    examples = [
        'What makes VIM-2 a good drug target?',
        'Why is NDM-1 considered nearly undruggable?',
        'What are key structural features of KPC-2 for inhibitor design?',
        'What is the mechanism of vancomycin resistance in VanA?',
        'What are recent strategies against carbapenem-resistant bacteria?',
        'How do efflux pumps contribute to multidrug resistance?',
        'What novel inhibitors target metallo-beta-lactamases?'
    ]
    example  = st.selectbox('Example questions', [''] + examples)
    question = st.text_input('Or type your own question')
    final_question = question if question else example
    if st.button('Ask ResistAI', type='primary') and final_question:
        with st.spinner('Searching literature and generating answer...'):
            articles = search_literature(final_question, n_results=n_results)
            answer   = ask_llm(final_question, articles)
        st.subheader('Answer')
        st.markdown(answer)
        st.subheader(f'Retrieved Literature ({len(articles)} articles)')
        for a in articles:
            with st.expander(f"[{a['score']}] {a['title'][:80]}..."):
                st.markdown(f"**PMID:** [{a['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{a['pmid']})")
                st.markdown(f"**Journal:** {a['journal']} | **Year:** {a['year']}")