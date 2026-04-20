import json
import chromadb
from sentence_transformers import SentenceTransformer

model      = SentenceTransformer('all-MiniLM-L6-v2')
client     = chromadb.PersistentClient(path='module2/data/chroma_db')
collection = client.get_collection('pubmed_articles')

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

def protein_query(gene, organism, family, n_results=10):
    query = f'{gene} {organism} antibiotic resistance mechanism drug target'
    return search_literature(query, n_results=n_results)

def format_context(articles):
    lines = []
    for a in articles:
        lines.append(
            f"- [PMID:{a['pmid']}] ({a['year']}) {a['title']} ({a['journal']}, relevance: {a['score']})"
        )
    return '\n'.join(lines)