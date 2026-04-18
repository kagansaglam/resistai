import json
import chromadb
from sentence_transformers import SentenceTransformer

print("[INFO] Loading articles...")
with open("module2/data/pubmed_articles.json") as f:
    articles = json.load(f)

print(f"[INFO] {len(articles)} articles loaded")
print("[INFO] Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="module2/data/chroma_db")

try:
    client.delete_collection("pubmed_articles")
except:
    pass
collection = client.create_collection(
    name="pubmed_articles",
    metadata={"hnsw:space": "cosine"}
)

BATCH_SIZE = 100
total = len(articles)

for i in range(0, total, BATCH_SIZE):
    batch = articles[i:i+BATCH_SIZE]

    texts = [
        f"{a['title']} {a['journal']} {a['year']}"
        for a in batch
    ]
    embeddings = model.encode(texts).tolist()

    collection.add(
        ids=[a["pmid"] for a in batch],
        embeddings=embeddings,
        documents=[a["title"] for a in batch],
        metadatas=[{
            "pmid":    a["pmid"],
            "journal": a["journal"],
            "year":    a["year"],
            "query":   a["query"]
        } for a in batch]
    )
print(f"[OK] Indexed {min(i+BATCH_SIZE, total)}/{total} articles")

print(f"\n[OK] ChromaDB ready — {collection.count()} articles indexed")
