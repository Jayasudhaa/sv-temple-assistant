"""
Local Testing Script for Food Query Retrieval
Run this to debug why "food" queries return no results
"""

import json
import sys

# Step 1: Check if meta.json has food-related content
print("="*80)
print("STEP 1: Checking meta.json for food-related content")
print("="*80)

try:
    with open("backend/faiss_store/meta.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        META = data.get("meta", [])
    
    print(f"✓ Loaded meta.json successfully")
    print(f"✓ Total chunks: {len(META)}")
    
    # Search for food keywords
    food_keywords = ["food", "cafeteria", "annadanam", "prasadam", "meal", "lunch"]
    food_chunks = []
    
    for keyword in food_keywords:
        count = 0
        for i, chunk in enumerate(META):
            if keyword.lower() in chunk.get("text", "").lower():
                count += 1
                if keyword == "cafeteria" or keyword == "annadanam":
                    food_chunks.append((keyword, i, chunk))
        print(f"  '{keyword}': {count} chunks found")
    
    print(f"\n✓ Found {len(food_chunks)} specific cafeteria/annadanam chunks")
    
    if len(food_chunks) > 0:
        print("\nSample food-related chunks:")
        for kw, idx, chunk in food_chunks[:3]:
            print(f"\n  Keyword: {kw}, Chunk #{idx}")
            print(f"  Text preview: {chunk['text'][:200]}...")
    else:
        print("\n✗ WARNING: No cafeteria/annadanam content found!")
        print("  → You need to add Annadanam_Food_Services.txt and re-embed")

except FileNotFoundError:
    print("✗ ERROR: meta.json not found at backend/faiss_store/meta.json")
    print("  Make sure you're running from project root directory")
    sys.exit(1)

# Step 2: Test query expansion
print("\n" + "="*80)
print("STEP 2: Testing Query Expansion Logic")
print("="*80)

try:
    # Load the expand_query function from retrieval.py
    with open("backend/retrieval.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    # Check if bidirectional mapping exists
    if 'any(var in query_lower for var in variations)' in code:
        print("✓ Bidirectional query expansion FOUND (FIXED version)")
    else:
        print("✗ OLD query expansion detected (NOT FIXED)")
        print("  → Replace retrieval.py with retrieval_FIXED.py")
    
    # Show the event_map section
    import re
    event_map_match = re.search(r'event_map = \{.*?\}', code, re.DOTALL)
    if event_map_match:
        print("\nEvent map in retrieval.py:")
        print(event_map_match.group(0)[:500] + "...")
        
        if '"food"' in event_map_match.group(0) or "'food'" in event_map_match.group(0):
            print("\n✓ 'food' keyword found in event_map")
        else:
            print("\n✗ 'food' keyword NOT in event_map variations")

except FileNotFoundError:
    print("✗ ERROR: retrieval.py not found")
    sys.exit(1)

# Step 3: Test without FAISS (keyword search only)
print("\n" + "="*80)
print("STEP 3: Testing Keyword Search (No Embeddings Required)")
print("="*80)

def simple_keyword_search(query, meta_data, k=5):
    """Simple keyword search without embeddings"""
    query_words = query.lower().split()
    results = []
    
    for chunk in meta_data:
        text_lower = chunk.get("text", "").lower()
        # Check if ANY query word appears in chunk
        if any(word in text_lower for word in query_words):
            results.append(chunk)
            if len(results) >= k:
                break
    
    return results

test_queries = ["food", "cafeteria", "annadanam", "lunch", "meal"]

for query in test_queries:
    results = simple_keyword_search(query, META, k=3)
    print(f"\nQuery: '{query}'")
    print(f"Results: {len(results)} chunks")
    
    if len(results) > 0:
        print(f"✓ Keyword search working for '{query}'")
        print(f"  First result: {results[0]['text'][:150]}...")
    else:
        print(f"✗ No results for '{query}' - content missing!")

# Step 4: Check if dependencies are installed
print("\n" + "="*80)
print("STEP 4: Checking Dependencies")
print("="*80)

dependencies = {
    "faiss": "faiss-cpu or faiss-gpu",
    "numpy": "numpy",
    "boto3": "boto3"
}

for module, package in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {module} installed")
    except ImportError:
        print(f"✗ {module} NOT installed - run: pip install {package}")

# Step 5: Provide next steps
print("\n" + "="*80)
print("SUMMARY & NEXT STEPS")
print("="*80)

print("\nTo fix the issue:")
print("\n1. If content is missing (no cafeteria/annadanam chunks):")
print("   → Add Annadanam_Food_Services.txt to data_raw/Services/")
print("   → Run: python backend/embeddings.py")
print("   → This will rebuild the vector store with food content")

print("\n2. If retrieval.py has old logic:")
print("   → Replace backend/retrieval.py with retrieval_FIXED.py")
print("   → This enables bidirectional query expansion")

print("\n3. To test full pipeline locally:")
print("   → Run: python test_local_retrieval.py (see next script)")

print("\n4. If all looks good but still fails:")
print("   → Check Lambda environment variables")
print("   → Verify boto3 can access Bedrock in Lambda")
print("   → Check CloudWatch logs for actual error messages")

print("\n" + "="*80)
