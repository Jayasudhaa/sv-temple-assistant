# backend/retrieval.py

import os
import json
import faiss
import numpy as np
from embeddings import embed_text_bedrock

BASE_DIR = os.path.dirname(__file__)
FAISS_DIR = os.path.join(BASE_DIR, "faiss_store")

FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
META_PATH = os.path.join(FAISS_DIR, "meta.json")

# We'll load index/meta once and reuse (good for Lambda warm starts)
_index = None
_meta = None

def _load_index_and_meta():
    global _index, _meta
    if _index is None or _meta is None:
        _index = faiss.read_index(FAISS_INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as mf:
            _meta = json.load(mf)
    return _index, _meta

def retrieve_chunks(question: str, k: int = 4):
    """
    Embed the question, run FAISS similarity, return top-k chunks.
    """
    index, meta = _load_index_and_meta()

    q_vec = np.array([embed_text_bedrock(question)], dtype="float32")

    distances, indices = index.search(q_vec, k)

    hits = []
    for rank, idx in enumerate(indices[0]):
        if 0 <= idx < len(meta):
            c = meta[idx].copy()
            c["_distance"] = float(distances[0][rank])
            hits.append(c)

    return hits
