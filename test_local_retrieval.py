"""
Complete Local Testing Script
Tests the full retrieval pipeline without Lambda/Bedrock
"""

import json
import numpy as np
import sys
import os

print("="*80)
print("TEMPLE CHATBOT - LOCAL RETRIEVAL TEST")
print("="*80)

# Configuration
FAISS_INDEX_PATH = "backend/faiss_store/index.faiss"
META_PATH = "backend/faiss_store/meta.json"

# Step 1: Load metadata
print("\n[1/5] Loading metadata...")
try:
    with open(META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        META = data.get("meta", [])
    print(f"✓ Loaded {len(META)} chunks from meta.json")
except FileNotFoundError:
    print(f"✗ ERROR: {META_PATH} not found")
    print("  Run this script from project root directory")
    sys.exit(1)

# Step 2: Implement query expansion (WITHOUT external imports)
print("\n[2/5] Testing query expansion...")

def expand_query_local(query):
    """Local version of expand_query for testing"""
    query_lower = query.lower()
    expansions = []
    
    # Event type expansions - BIDIRECTIONAL
    event_map = {
        "abhishekam": ["abhishekam", "sacred bathing", "abhisheka"],
        "pooja": ["pooja", "puja", "worship", "archana"],
        "festival": ["festival", "celebration", "utsavam"],
        "vratam": ["vratam", "vrata", "fasting"],
        "homam": ["homam", "homa", "fire ceremony", "fire ritual"],
        "kalyanam": ["kalyanam", "wedding", "divine marriage"],
        "annadanam": ["annadanam", "prasadam", "food", "cafeteria", "blessed food", "free meal", "lunch", "dinner", "cooked food", "meal"],
    }
    
    # Check both keys AND values (BIDIRECTIONAL)
    for event_key, variations in event_map.items():
        if event_key in query_lower or any(var in query_lower for var in variations):
            expansions.extend([event_key] + variations)
            break
    
    # Build expanded query
    if expansions:
        unique_expansions = list(set(expansions))[:8]
        expanded = query + " " + " ".join(unique_expansions)
    else:
        expanded = query
    
    return expanded

# Test queries
test_queries = [
    "food",
    "cafeteria", 
    "annadanam",
    "when is lunch served",
    "cooked food"
]

print("\nQuery Expansion Results:")
for query in test_queries:
    expanded = expand_query_local(query)
    print(f"\n  '{query}'")
    print(f"  → '{expanded}'")
    
    # Check if expansion happened
    if len(expanded.split()) > len(query.split()):
        print(f"  ✓ Expanded successfully")
    else:
        print(f"  ✗ No expansion (problem!)")

# Step 3: Keyword-based search (no FAISS needed)
print("\n[3/5] Testing keyword search...")

def search_by_keywords_local(query, meta_data, k=7):
    """Keyword search without FAISS"""
    query_lower = query.lower()
    query_words = query_lower.split()
    
    results = []
    
    # Expand query first
    expanded = expand_query_local(query)
    all_keywords = expanded.lower().split()
    
    for chunk in meta_data:
        text_lower = chunk.get("text", "").lower()
        
        # Check if ANY keyword appears
        if any(kw in text_lower for kw in all_keywords):
            # Calculate match score
            match_count = sum(1 for kw in all_keywords if kw in text_lower)
            results.append((match_count, chunk))
    
    # Sort by match count (highest first)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Return top k
    return [chunk for score, chunk in results[:k]]

print("\nKeyword Search Results:")
for query in test_queries:
    results = search_by_keywords_local(query, META, k=5)
    print(f"\n  Query: '{query}'")
    print(f"  Found: {len(results)} chunks")
    
    if len(results) > 0:
        print(f"  ✓ SUCCESS - Top result:")
        print(f"    {results[0]['text'][:150]}...")
    else:
        print(f"  ✗ FAILED - No results (content missing)")

# Step 4: Hybrid search simulation
print("\n[4/5] Testing hybrid search (keyword fallback)...")

def hybrid_search_local(query, meta_data, k=7):
    """Simulate hybrid search without embeddings"""
    # For local testing, we only use keyword search
    # In production, semantic search would run first
    
    food_keywords = ["food", "cafeteria", "annadanam", "prasadam", "meal", "lunch", "dinner"]
    is_food_query = any(kw in query.lower() for kw in food_keywords)
    
    # Get keyword results
    keyword_results = search_by_keywords_local(query, meta_data, k=k)
    
    if is_food_query and len(keyword_results) < 3:
        # Aggressive fallback for food queries
        print(f"    Food query detected - using aggressive search")
        
        # Add explicit food keywords
        enhanced_query = query + " annadanam prasadam cafeteria food meal"
        keyword_results = search_by_keywords_local(enhanced_query, meta_data, k=10)
    
    return keyword_results[:k]

print("\nHybrid Search Results:")
for query in test_queries:
    results = hybrid_search_local(query, META, k=5)
    print(f"\n  Query: '{query}'")
    print(f"  Found: {len(results)} chunks")
    
    if len(results) > 0:
        print(f"  ✓ Top 3 results:")
        for i, chunk in enumerate(results[:3], 1):
            print(f"    {i}. {chunk['text'][:100]}...")
    else:
        print(f"  ✗ No results")

# Step 5: Analyze content coverage
print("\n[5/5] Analyzing food content coverage...")

food_keywords = {
    "cafeteria": 0,
    "annadanam": 0,
    "prasadam": 0,
    "food": 0,
    "meal": 0,
    "lunch": 0,
    "dinner": 0
}

for chunk in META:
    text_lower = chunk.get("text", "").lower()
    for keyword in food_keywords:
        if keyword in text_lower:
            food_keywords[keyword] += 1

print("\nFood Content Coverage:")
total_food_chunks = 0
for keyword, count in food_keywords.items():
    print(f"  {keyword:15s}: {count:3d} chunks")
    total_food_chunks += count

print(f"\n  Total food-related: {total_food_chunks} chunks")
print(f"  Total all chunks:   {len(META)} chunks")
print(f"  Coverage:           {(total_food_chunks/len(META)*100):.1f}%")

# Final diagnosis
print("\n" + "="*80)
print("DIAGNOSIS & RECOMMENDATIONS")
print("="*80)

if total_food_chunks < 5:
    print("\n🔴 CRITICAL: Insufficient food content!")
    print("\n   Problem: Only", total_food_chunks, "chunks contain food-related keywords")
    print("   Solution:")
    print("   1. Add Annadanam_Food_Services.txt to your data_raw/Services/ folder")
    print("   2. Run: python backend/embeddings.py")
    print("   3. This will add 15-20 food-related chunks")
    print("   4. Re-run this test script to verify")

elif food_keywords["cafeteria"] == 0:
    print("\n🟡 WARNING: No cafeteria content found")
    print("   Even if annadanam exists, users asking 'cafeteria' get nothing")
    print("   Add content that explicitly mentions 'cafeteria hours'")

else:
    print("\n✅ GOOD: Sufficient food content exists")
    print(f"   {total_food_chunks} chunks available")
    
    if any(len(hybrid_search_local(q, META)) == 0 for q in test_queries):
        print("\n🟡 But some queries still fail!")
        print("   Problem likely in:")
        print("   1. Query expansion not working (check retrieval.py)")
        print("   2. Bedrock embedding issues (check AWS credentials)")
        print("   3. FAISS index not matching properly")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)

print("\n1. If content is missing:")
print("   cd data_raw/")
print("   mkdir -p Services")
print("   # Copy Annadanam_Food_Services.txt to Services/")
print("   cd ..")
print("   python backend/embeddings.py")

print("\n2. If retrieval.py needs update:")
print("   cp backend/retrieval.py backend/retrieval_OLD.py")
print("   cp retrieval_FIXED.py backend/retrieval.py")

print("\n3. Test with actual embeddings (if FAISS installed):")
print("   python test_with_embeddings.py")

print("\n4. Test full Lambda locally:")
print("   sam local invoke TempleAssistant --event test-event.json")

print("\n5. Check actual Lambda logs:")
print("   aws logs tail /aws/lambda/your-function-name --follow")

print("\n" + "="*80)

# Save results to file for reference
with open("test_results.txt", "w") as f:
    f.write("Food Query Test Results\n")
    f.write("="*80 + "\n\n")
    f.write(f"Total chunks: {len(META)}\n")
    f.write(f"Food-related chunks: {total_food_chunks}\n\n")
    
    f.write("Query Test Results:\n")
    for query in test_queries:
        results = hybrid_search_local(query, META, k=5)
        f.write(f"\nQuery: '{query}'\n")
        f.write(f"Results: {len(results)}\n")
        if results:
            f.write(f"Top result: {results[0]['text'][:100]}...\n")

print("\n✓ Results saved to test_results.txt")
