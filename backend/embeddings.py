import boto3, json, os, numpy as np

client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
MODEL = os.getenv("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

def embed(texts):
    if isinstance(texts, str): texts = [texts]
    vecs = []
    for t in texts:
        resp = client.invoke_model(
            modelId=MODEL,
            body=json.dumps({"inputText": t}),
            contentType="application/json",
            accept="application/json"
        )
        vecs.append(json.loads(resp["body"].read())["embedding"])
    return np.array(vecs, dtype="float32")