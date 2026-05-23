"""
Index ESM-2 embeddings into ChromaDB for similarity search.
"""
import os
import pandas as pd
import chromadb
from pathlib import Path

PARQUET = os.path.expanduser("~/resistai/data/embeddings.parquet")
CHROMA_PATH = os.path.expanduser("~/resistai-api/data/chroma_esm")
ANNOTATED = os.path.expanduser("~/resistai-api/data/proteins_annotated.csv")

print("Loading embeddings...")
df = pd.read_parquet(PARQUET)
meta_df = pd.read_csv(ANNOTATED)
meta = {row['uniprot_id']: row for _, row in meta_df.iterrows()}

feat_cols = [c for c in df.columns if c != 'uniprot_id']
print(f"Loaded {len(df)} proteins, {len(feat_cols)} dims")

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Delete if exists, recreate
try:
    client.delete_collection("esm_embeddings")
except:
    pass
collection = client.create_collection("esm_embeddings", metadata={"hnsw:space": "cosine"})

BATCH = 100
for i in range(0, len(df), BATCH):
    batch = df.iloc[i:i+BATCH]
    ids = batch['uniprot_id'].tolist()
    embeddings = batch[feat_cols].values.tolist()
    metadatas = []
    for uid in ids:
        m = meta.get(uid, {})
        metadatas.append({
            "uniprot_id": uid,
            "gene": str(m.get("gene", "")),
            "organism": str(m.get("organism", ""))[:100],
            "family": str(m.get("family", "")),
            "best_score": float(m.get("best_score", 0)),
        })
    collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
    print(f"Indexed {min(i+BATCH, len(df))}/{len(df)}")

print(f"Done. Total indexed: {collection.count()}")
