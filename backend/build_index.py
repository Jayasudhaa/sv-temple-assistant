# backend/build_index.py

import os
import glob
import json
import faiss
import numpy as np
from embeddings import embed_text_bedrock, chunk_text

BASE_DIR = os.path.dirname(__file__)
DATA_RAW_DIR = os.path.join(BASE_DIR, "..", "data_raw")
FAISS_DIR = os.path.join(BASE_DIR, "faiss_store")

os.makedirs(FAISS_DIR, exist_ok=True)

FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
META_PATH = os.path.join(FAISS_DIR, "meta.json")

def load_all_txt():
    """
    Read every .txt file in data_raw/.
    Returns list[(filename, text)].
    """
    texts = []
    pattern = os.path.join(DATA_RAW_DIR, "*.txt")
    for path in glob.glob(pattern):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        texts.append((filename, txt))
    return texts

def main():
    docs = load_all_txt()

    all_chunks = []
    vectors = []

    # 1. chunk and collect all text pieces
    for (name, txt) in docs:
        chs = chunk_text(txt, source_name=name)
        for c in chs:
            all_chunks.append(c)

    # 2. embed each chunk
    for c in all_chunks:
        vec = embed_text_bedrock(c["text"])
        vectors.append(vec)

    vectors_np = np.array(vectors).astype("float32")

    # 3. build FAISS index
    dim = vectors_np.shape[1]  # vector dimension
    index = faiss.IndexFlatL2(dim)
    index.add(vectors_np)

    # 4. save FAISS index + metadata
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(META_PATH, "w", encoding="utf-8") as mf:
        json.dump(all_chunks, mf, ensure_ascii=False, indent=2)

    print(f"Indexed {len(all_chunks)} chunks. Saved to {FAISS_DIR}")

if __name__ == "__main__":
    main()
