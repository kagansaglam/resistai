import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv('/home/kagan/resistai/.env')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

st.set_page_config(page_title='ResistAI', page_icon='🧬', layout='wide')
st.title('🧬 ResistAI — Antibiotic Resistance Research Assistant')
st.caption('Powered by PubMed RAG + Llama 3.3 | 949 articles indexed')

@st.cache_resource
def load_rag():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path='module2/data/chroma_db')
    collection = client.get_collection('pubmed_articles')
    return model, collection

model, collection = load_rag()

def search_literature(query, n_results=10):
    embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=n_results)
    articles = []
    for i, doc in enumerate(results['documents'][0]):
        meta = results['metadatas'][0][i]
        articles.append({
            'title': doc,
            'pmid': meta['pmid'],
            'journal': meta['journal'],
            'year': meta['year'],
            'score': round(1 - results['distances'][0][i], 3)
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
    st.header('About')
    st.markdown('ResistAI analyses 949 PubMed articles on WHO priority pathogens using semantic search and Llama 3.3.')
    st.divider()
    st.header('Protein Summary')
    proteins = {
        'Q9HYD3': ('VIM-2',  'P. aeruginosa', 0.755, 'high'),
        'P25051': ('VanA',   'E. faecium',    0.566, 'medium'),
        'Q9F663': ('KPC-2',  'K. pneumoniae', 0.427, 'medium'),
        'Q9KLB7': ('OXA-23', 'A. baumannii',  0.180, 'low'),
        'B9A8S5': ('NDM-1',  'E. coli',       0.168, 'low'),
    }
    for uid, (gene, org, score, tier) in proteins.items():
        color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}[tier]
        st.markdown(f'{color} **{gene}** — {org} (score: {score})')
    st.divider()
    n_results = st.slider('Articles to retrieve', 5, 20, 10)

st.subheader('Ask a research question')
examples = [
    'What makes VIM-2 a good drug target?',
    'Why is NDM-1 considered nearly undruggable?',
    'What are key structural features of KPC-2 for inhibitor design?',
    'What is the mechanism of vancomycin resistance in VanA?',
    'What are recent strategies against carbapenem-resistant bacteria?'
]
example = st.selectbox('Example questions', [''] + examples)
question = st.text_input('Or type your own question')
final_question = question if question else example

if st.button('Ask ResistAI', type='primary') and final_question:
    with st.spinner('Searching literature and generating answer...'):
        articles = search_literature(final_question, n_results=n_results)
        answer = ask_llm(final_question, articles)
    st.subheader('Answer')
    st.markdown(answer)
    st.subheader(f'Retrieved Literature ({len(articles)} articles)')
    for a in articles:
        with st.expander(f"[{a['score']}] {a['title'][:80]}..."):
            st.markdown(f"**PMID:** [{a['pmid']}](https://pubmed.ncbi.nlm.nih.gov/{a['pmid']})")
            st.markdown(f"**Journal:** {a['journal']}")
            st.markdown(f"**Year:** {a['year']}")
            st.markdown(f"**Relevance score:** {a['score']}")