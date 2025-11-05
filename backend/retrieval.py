import faiss, json, numpy as np
from .embeddings import embed

index = faiss.read_index("backend/faiss_store/index.faiss")
with open("backend/faiss_store/meta.json") as f:
    META = json.load(f)["meta"]

def get_chunks(question, k=3):
    q_vec = embed(question)[0:1]
    D, I = index.search(q_vec, k)
    return [META[i] for i in I[0]]