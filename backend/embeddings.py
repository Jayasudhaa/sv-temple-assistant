# backend/embeddings.py

import boto3
import json

# Configure your region here.
BEDROCK_REGION = "us-east-1"

# Titan text embedding model ID (example; pick the one you enabled in Bedrock).
EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"

bedrock_runtime = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def embed_text_bedrock(text: str) -> list[float]:
    """
    Call Bedrock Titan Embeddings to turn text into a vector.
    Returns a Python list[float].
    """
    body = {
        "inputText": text
    }

    response = bedrock_runtime.invoke_model(
        modelId=EMBED_MODEL_ID,
        body=json.dumps(body)
    )

    response_body = json.loads(response["body"].read())

    # Titan returns the embedding vector usually under "embedding"
    # If model shape changes, update this field accordingly.
    embedding = response_body["embedding"]
    return embedding

def chunk_text(doc_text: str, source_name: str, max_chars: int = 500):
    """
    Break a long text into ~500 char chunks with metadata.
    Returns list[dict] like:
      { "text": "...", "source": "hours.txt" }
    """
    chunks = []
    start = 0
    while start < len(doc_text):
        end = start + max_chars
        piece = doc_text[start:end].strip()
        if piece:
            chunks.append({
                "text": piece,
                "source": source_name
            })
        start = end
    return chunks

