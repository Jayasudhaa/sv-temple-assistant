import os
import json
from pathlib import Path
import boto3
import numpy as np
import faiss

DATA_DIR = Path("data_raw")
FAISS_DIR = Path("backend/faiss_store")
FAISS_DIR.mkdir(parents=True, exist_ok=True)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# -------- LOAD + CHUNK TXT FILES (RECURSIVE) ----------
def load_all_text_chunks():
    chunks = []
    sources = []

    # Recursively read ALL .txt files in data_raw
    for file in DATA_DIR.rglob("*.txt"):
        text = file.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue

        # Simple chunking: by blank line
        parts = [p.strip() for p in text.split("\n") if p.strip()]

        for p in parts:
            if len(p) > 10:  # discard very short noise lines
                chunks.append(p)
                sources.append(str(file))

    return chunks, sources


# ---------- EMBEDDINGS -------------
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


# ---------- BUILD INDEX -------------
def build_index():
    print("Loading and chunking text…")
    chunks, sources = load_all_text_chunks()
    print("Total chunks:", len(chunks))

    if len(chunks) == 0:
        raise Exception("❌ No chunks found! Check your data_raw/ folder structure.")

    # embed in batches
    vectors = []
    batch_size = 32

    print("Embedding chunks with Bedrock…")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        embeds = embed_bedrock(batch)
        vectors.extend(embeds)

    vectors = np.array(vectors, dtype="float32")
    dim = vectors.shape[1]

    # FAISS index
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    print("Saving FAISS index…")
    faiss.write_index(index, str(FAISS_DIR / "index.faiss"))

    print("Saving metadata…")
    meta = []
    for i, text in enumerate(chunks):
        meta.append({"id": i, "source": sources[i], "text": text})

    with open(FAISS_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta}, f, indent=2)

    print("🎉 DONE — FAISS index built successfully!")


if __name__ == "__main__":
    build_index()
