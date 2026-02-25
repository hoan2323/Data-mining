import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

RAW_CSV    = r"C:\Users\hn745\Documents\DPM302m\projecDBM\datasource\laptop_data_clear.csv"
CHROMA_DIR = "./chroma_db"
COLLECTION = "laptops"
MODEL_NAME = "intfloat/multilingual-e5-large"
BATCH_SIZE = 16



def load_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV, on_bad_lines="skip", engine="python")

    df = df[df["brand"] != "brand"]                                         
    df = df[df["mo_ta"].notna() & (df["mo_ta"].str.strip() != "")]           

    for col in ["price", "ram", "storage", "screen_size"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["rating"] = df["rating"].fillna(df["rating"].median())             
    df["gpu_type"] = df["gpu"].apply(
        lambda g: "dedicated" if "card rời" in str(g).lower() else "integrated"
    )

    return df.reset_index(drop=True)


def embed_texts(texts: list[str], model: SentenceTransformer) -> list:
    all_embeddings = []
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding"):
        batch = [f"passage: {t}" for t in texts[i : i + BATCH_SIZE]]
        embs  = model.encode(batch, normalize_embeddings=True).tolist()
        all_embeddings.extend(embs)
    return all_embeddings


def save_to_chromadb(df: pd.DataFrame, embeddings: list):
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
        print(f"[INFO] Đã xoá collection cũ: {COLLECTION}")

    collection = client.create_collection(
        name     = COLLECTION,
        metadata = {"hnsw:space": "cosine"}
    )

    ids       = df.index.astype(str).tolist()
    documents = df["mo_ta"].tolist()
    metadatas = [
        {
            "brand": str(row["brand"]),
            "name": str(row["name"]),
            "cpu": str(row["cpu"]),
            "gpu": str(row["gpu"]),
            "gpu_type" : str(row["gpu_type"]),
            "ram": float(row["ram"]),
            "storage" : float(row["storage"]),
            "screen_size": float(row["screen_size"]),
            "price": float(row["price"]),
            "rating": float(row["rating"]),
        }
        for _, row in df.iterrows()
    ]

    for i in range(0, len(ids), BATCH_SIZE):
        collection.add(
            ids        = ids[i : i + BATCH_SIZE],
            documents  = documents[i : i + BATCH_SIZE],
            metadatas  = metadatas[i : i + BATCH_SIZE],
            embeddings = embeddings[i : i + BATCH_SIZE],
        )

    print(f" Đã lưu {collection.count()} vectors → {CHROMA_DIR}")



if __name__ == "__main__":
    print("Loading data...")
    df = load_data()
    print(f"{len(df)} laptops sẵn sàng")

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = embed_texts(df["mo_ta"].tolist(), model)

    print("Saving to ChromaDB...")
    save_to_chromadb(df, embeddings)
