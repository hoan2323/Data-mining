import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np

# ===== LOAD & EMBED =====
df = pd.read_csv("laptop_with_description.csv")
print(f"Loaded {len(df)} laptops")

model = SentenceTransformer('intfloat/multilingual-e5-large')
embeddings = model.encode(df['mo_ta'].tolist(), show_progress_bar=True)

# ===== CHROMADB =====
chroma_client = chromadb.Client(Settings(allow_reset=True))
try:
    chroma_client.delete_collection("laptop_e5_fixed")
except:
    pass

collection = chroma_client.create_collection("laptop_e5_fixed")

metadata_cols = [col for col in df.columns if col != 'mo_ta']
metadatas = df[metadata_cols].to_dict('records')

for meta in metadatas:
    for k, v in meta.items():
        if isinstance(v, (np.integer, np.floating)):
            meta[k] = float(v)
        if pd.isna(v):
            meta[k] = ""

collection.add(
    ids=[f"laptop_{i}" for i in range(len(df))],
    embeddings=embeddings.tolist(),
    documents=df['mo_ta'].tolist(),
    metadatas=metadatas
)

# ===== FIXED QUERY FUNCTION =====
def search_laptops_e5(query, top_k=5, filters=None):
    query_emb = model.encode([f"query: {query}"]).tolist()
    
    # FIX: where=None nếu không filters
    where = filters if filters else None
    
    results = collection.query(
        query_embeddings=query_emb,
        n_results=top_k,
        where=where
    )
    
    recs = []
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        recs.append({
            'name': meta.get('name', '?'),
            'brand': meta.get('brand', '?'),
            'price': meta.get('price', 0),
            'rating': meta.get('rating', 0),
            'similarity': 1 - results['distances'][0][i],
            'mo_ta_preview': results['documents'][0][i][:250] + "...",
            'review': meta.get('review_text', '')
        })
    return recs

# ===== TEST =====
test_queries = [
    
    "laptop văn phòng mạnh mẽ trên 30 triệu của apple"
]

for q in test_queries:
    print(f"\n🔍 '{q}'")
    results = search_laptops_e5(q, top_k=1)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name'][:60]} ({r['brand']})")
        print(f"   Giá: {r['price']:,.0f}đ | Sim: {r['similarity']:.3f}")
        print(f"   Preview: {r['mo_ta_preview']}\n")

print("✅ FIXED & READY!")
