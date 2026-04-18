import json
import chromadb
from sentence_transformers import SentenceTransformer

model  = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="module2/data/chroma_db")
collection = client.get_collection("pubmed_articles")


def search_literature(query, n_results=10):
    embedding = model.encode([query]).tolist()
    results   = collection.query(
        query_embeddings=embedding,
        n_results=n_results
    )
    articles = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        articles.append({
            "title":   doc,
            "pmid":    meta["pmid"],
            "journal": meta["journal"],
            "year":    meta["year"],
            "score":   round(1 - results["distances"][0][i], 3)
        })
    return articles


def format_context(articles):
    lines = []
    for a in articles:
        lines.append(
            f"[PMID:{a['pmid']}] ({a['year']}) {a['title']} "
            f"— {a['journal']} (relevance: {a['score']})"
        )
    return "\n".join(lines)
def ask(question, n_results=10):
    articles = search_literature(question, n_results=n_results)
    context  = format_context(articles)

    print(f"\n[QUERY] {question}")
    print(f"[CONTEXT] Top {len(articles)} relevant articles:")
    print(context)
    return articles, context


if __name__ == "__main__":
    ask("What is the druggability of VIM-2 metallo-beta-lactamase?")
    ask("NDM-1 structure and drug binding sites")
    ask("KPC-2 carbapenemase inhibitor development")
