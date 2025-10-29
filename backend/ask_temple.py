# backend/ask_temple.py

import os
import json
import boto3
from retrieval import retrieve_chunks

BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(BASE_DIR, "..", "config")

SYSTEM_PROMPT_PATH = os.path.join(CONFIG_DIR, "system_prompt.txt")
STATUS_PATH = os.path.join(CONFIG_DIR, "temple_status.json")

BEDROCK_REGION = "us-east-1"
LLM_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # example fast/cheap model in Bedrock

bedrock_runtime = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def load_status():
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_user_prompt(status_info: dict, chunks: list[dict], user_question: str) -> str:
    """
    Create one big prompt string for the model.
    We include:
    - Temple status (open/closed)
    - Retrieved context chunks
    - User's actual question
    - Instructions
    """
    status_block = (
        "TEMPLE STATUS:\n"
        f"{status_info.get('message','')}\n"
        f"Next: {status_info.get('next_open_time','')}\n\n"
    )

    context_block_lines = []
    for c in chunks:
        context_block_lines.append(
            f"[Source: {c['source']}]\n{c['text']}\n"
        )
    context_block = "\n".join(context_block_lines)

    instructions = (
        "Answer ONLY using Temple Status and Context above. "
        "If the answer is not found, say: "
        "\"Please contact a temple volunteer for this request.\" "
        "Never invent times, phone numbers, or prices."
    )

    user_block = (
        status_block +
        "CONTEXT FROM TEMPLE DOCUMENTS:\n" +
        context_block +
        "\nUSER QUESTION:\n" +
        user_question +
        "\n\n" +
        "INSTRUCTIONS:\n" +
        instructions
    )

    return user_block

def call_bedrock_chat(system_prompt: str, user_prompt: str) -> str:
    """
    Call Bedrock chat model (Anthropic Claude style).
    Different models have slightly different request/response schema.
    We'll build Anthropic-style body that Bedrock expects.
    """
    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }

    response = bedrock_runtime.invoke_model(
        modelId=LLM_MODEL_ID,
        body=json.dumps(body)
    )

    resp_body = json.loads(response["body"].read())

    # For Claude models in Bedrock, response["body"] usually decodes to a dict
    # whose text output is in something like resp_body["output"][0]["content"][0]["text"].
    # We'll code defensively:
    try:
        answer_text = resp_body["output"][0]["content"][0]["text"]
    except Exception:
        # fallback if Bedrock model returns in a different field
        answer_text = json.dumps(resp_body)

    return answer_text.strip()

def answer_user(question_text: str) -> str:
    """
    Public function you'll call from Lambda.
    """
    status_info = load_status()
    system_prompt = load_system_prompt()

    # get top chunks from FAISS
    chunks = retrieve_chunks(question_text, k=4)

    # build the user message for the LLM
    user_prompt = build_user_prompt(status_info, chunks, question_text)

    # ask the model
    llm_answer = call_bedrock_chat(system_prompt, user_prompt)

    if not llm_answer.strip():
        return "Please contact a temple volunteer for this request."

    return llm_answer
