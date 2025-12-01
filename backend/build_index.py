import os
import json
import pickle
from pathlib import Path
import boto3
import numpy as np
import faiss

# -------------------------------
# Paths
# -------------------------------
DATA_DIR = Path("data_raw")
FAISS_DIR = Path("backend/faiss_store")
FAISS_DIR.mkdir(parents=True, exist_ok=True)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# -------------------------------
# Clean text loader
# -------------------------------
def load_all_text_chunks():
    chunks = []
    sources = []

    for file in DATA_DIR.rglob("*.txt"):
        content = file.read_text(encoding="utf-8", errors="ignore")

        # Simple chunking: split by blank lines
        parts = [p.strip() for p in content.split("\n") if p.strip()]

        for p in parts:
            if len(p) > 10:
                chunks.append(p)
                sources.append(str(file))

    return chunks, sources


# -------------------------------
# Bedrock embedding
# -------------------------------
def embed_bedrock(text_list):
    body = {
        "texts": text_list,
        "input_type": "search_document"
    }

    resp = bedrock.invoke_model(
        modelId="cohere.embed-english-v3",
        body=json.dumps(body),
        contentType="application/json"
    )

    data = json.loads(resp["body"].read())
    return data["embeddings"]


# -------------------------------
# Index builder
# -------------------------------
def build_index():
    print("📥 Loading text files…")
    chunks, sources = load_all_text_chunks()
    print("Total chunks:", len(chunks))

    batch_size = 32
    vectors = []

    print("🧠 Generating embeddings (Cohere v3)…")
    for i in range(0, len(chunks), batch_size):
        sub = chunks[i:i+batch_size]
        embeds = embed_bedrock(sub)
        vectors.extend(embeds)

    vectors = np.array(vectors).astype("float32")
    dim = vectors.shape[1]

    print("📦 Building FAISS index…")
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save FAISS index
    faiss.write_index(index, str(FAISS_DIR / "index.faiss"))

    # Save metadata
    meta = []
    for i in range(len(chunks)):
        meta.append({
            "id": i,
            "source": sources[i],
            "text": chunks[i]
        })

    with open(FAISS_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta}, f, indent=2)

    print("✅ DONE — FAISS index and metadata created successfully!")


if __name__ == "__main__":
    build_index()
