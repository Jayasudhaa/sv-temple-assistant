# update_meta.py — Run this EVERY TIME you change any .txt file
import os, json
from backend.embeddings import embed

INPUT_DIR = "data_raw"
OUT_DIR = "backend/faiss_store"
os.makedirs(OUT_DIR, exist_ok=True)

texts = []
meta = []

print("Reading all .txt files from data_raw/...")
for file in sorted(os.listdir(INPUT_DIR)):
    if not file.endswith(".txt"): continue
    path = os.path.join(INPUT_DIR, file)
    raw = open(path, "r", encoding="utf-8").read()

    # Split into 600-char chunks
    chunks = [raw[i:i+600] for i in range(0, len(raw), 500)]
    for i, c in enumerate(chunks):
        texts.append(c)
        meta.append({
            "source": file,
            "chunk_id": i,
            "text": c
        })

print(f"Embedding {len(texts)} chunks...")
vecs = embed(texts)

print("Building FAISS index...")
import faiss
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

print("Saving index + meta...")
faiss.write_index(index, os.path.join(OUT_DIR, "index.faiss"))
json.dump({"meta": meta}, open(os.path.join(OUT_DIR, "meta.json"), "w"), indent=2)

print("meta.json UPDATED! Run build_tiny.py and upload ZIP.")