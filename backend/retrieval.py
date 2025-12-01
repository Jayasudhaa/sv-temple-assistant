import json
import faiss
import numpy as np
import boto3

# Load FAISS index + metadata
faiss_index = faiss.read_index("backend/faiss_store/index.faiss")

with open("backend/faiss_store/meta.json", "r", encoding="utf-8") as f:
    META = json.load(f)["meta"]

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def embed_query_bedrock(text):
    """Embed a single query string."""
    body = {
        "texts": [text],
        "input_type": "search_query"
    }

    resp = bedrock.invoke_model(
        modelId="cohere.embed-english-v3",
        body=json.dumps(body),
        contentType="application/json"
    )

    data = json.loads(resp["body"].read())
    return np.array(data["embeddings"], dtype="float32")


def get_chunks(query, k=7):
    """Retrieve top-k most relevant chunks."""
    if not query.strip():
        return []

    q_vec = embed_query_bedrock(query)
    D, I = faiss_index.search(q_vec.reshape(1, -1), k)

    return [META[i] for i in I[0] if 0 <= i < len(META)]
