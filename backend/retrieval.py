import json
import faiss
import numpy as np
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

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


def expand_query(query):
    """
    Expand query with synonyms and context for better retrieval
    """
    query_lower = query.lower()
    expansions = []
    
    # Deity name expansions
    deity_map = {
        "hanuman": ["hanuman", "anjaneya", "maruti"],
        "ganesha": ["ganesha", "ganapathi", "vinayaka", "ganesh"],
        "shiva": ["shiva", "siva", "maheswara", "rudra"],
        "vishnu": ["vishnu", "venkateswara", "venkateshwara", "srinivasa"],
        "lakshmi": ["lakshmi", "mahalakshmi", "sri devi"],
        "saraswati": ["saraswati", "sarada"],
        "murugan": ["murugan", "subramanya", "kartikeya"],
        "sai baba": ["sai baba", "shirdi sai", "sai"],
        "andal": ["andal", "goda devi"]
    }
    
    # Add deity variations
    for deity, variations in deity_map.items():
        if deity in query_lower:
            expansions.extend(variations)
    
    # Month expansions - include current month context
    now = datetime.now(ZoneInfo("America/Denver"))
    current_month = now.strftime("%B").lower()
    
    month_keywords = ["january", "february", "march", "april", "may", "june",
                     "july", "august", "september", "october", "november", "december"]
    
    month_in_query = False
    for month in month_keywords:
        if month in query_lower:
            expansions.append(month)
            month_in_query = True
            break
    
    # If asking about dates but no month specified, add current month
    date_keywords = ["when", "date", "schedule", "full moon", "purnima", "ekadasi"]
    if not month_in_query and any(kw in query_lower for kw in date_keywords):
        expansions.append(current_month)
    
    # Event type expansions
    event_map = {
        "abhishekam": ["abhishekam", "sacred bathing", "abhisheka"],
        "pooja": ["pooja", "puja", "worship", "archana"],
        "festival": ["festival", "celebration", "utsavam"],
        "vratam": ["vratam", "vrata", "fasting"],
        "homam": ["homam", "homa", "fire ceremony", "fire ritual"],
        "kalyanam": ["kalyanam", "wedding", "divine marriage", "celestial wedding"],
        "annadanam": ["annadanam", "prasadam", "food", "cafeteria", "blessed food", "free meal"],
        "deepavali":["diwali","deepavali habba", "festival of lights", "diya festival"]
    }
    
    for event, variations in event_map.items():
        if event in query_lower:
            expansions.extend(variations)
    
    # Day of week expansions for abhishekam queries
    day_map = {
        "monday": ["monday", "somavara", "1st week", "2nd week", "3rd week", "4th week"],
        "saturday": ["saturday", "1st saturday", "2nd saturday", "3rd saturday", "4th saturday"],
        "sunday": ["sunday", "1st sunday", "2nd sunday", "3rd sunday", "4th sunday"],
        "friday": ["friday", "3rd friday"]
    }
    
    for day, variations in day_map.items():
        if day in query_lower:
            expansions.extend(variations)
    
    # Build expanded query
    expanded = query
    if expansions:
        # Add most relevant expansions (limit to avoid over-expansion)
        unique_expansions = list(set(expansions))[:5]
        expanded = query + " " + " ".join(unique_expansions)
    
    return expanded


def get_chunks(query, k=7):
    """
    Retrieve top-k most relevant chunks with query expansion
    """
    if not query.strip():
        return []
    
    # Expand query for better semantic matching
    expanded_query = expand_query(query)
    
    # Embed the expanded query
    q_vec = embed_query_bedrock(expanded_query)
    
    # Search FAISS index
    D, I = faiss_index.search(q_vec.reshape(1, -1), k)
    
    # Return matched chunks
    chunks = [META[i] for i in I[0] if 0 <= i < len(META)]
    
    # Debug print (remove in production)
    print(f"Query: {query}")
    print(f"Expanded: {expanded_query}")
    print(f"Retrieved {len(chunks)} chunks")
    
    return chunks


def search_by_keywords(keywords, k=10):
    """
    Fallback: keyword-based search in metadata
    Useful when semantic search fails
    """
    results = []
    keywords_lower = [kw.lower() for kw in keywords]
    
    for item in META:
        text_lower = item["text"].lower()
        
        # Check if ALL keywords present
        if all(kw in text_lower for kw in keywords_lower):
            results.append(item)
            if len(results) >= k:
                break
    
    return results


def hybrid_search(query, k=7):
    """
    Combines semantic (FAISS) + keyword search for best results
    """
    # Try semantic search first
    semantic_results = get_chunks(query, k=k)
    
    # If semantic search returns few results, supplement with keyword search
    if len(semantic_results) < 3:
        # Extract key terms from query
        query_words = query.lower().split()
        important_words = [w for w in query_words if len(w) > 3]
        
        keyword_results = search_by_keywords(important_words, k=5)
        
        # Combine results (deduplicate by text)
        seen_texts = {chunk["text"] for chunk in semantic_results}
        for kw_chunk in keyword_results:
            if kw_chunk["text"] not in seen_texts:
                semantic_results.append(kw_chunk)
                seen_texts.add(kw_chunk["text"])
    
    return semantic_results[:k]
