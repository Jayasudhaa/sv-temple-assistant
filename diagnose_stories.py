#!/usr/bin/env python3
"""
Diagnostic script to check if story files are in FAISS index
Run this on your Windows machine in the project directory
"""

import json
from pathlib import Path

# Check if meta.json exists
meta_file = Path("backend/faiss_store/meta.json")

if not meta_file.exists():
    print("❌ ERROR: meta.json not found!")
    print("   Run: python build.py first")
    exit(1)

# Load metadata
with open(meta_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

chunks = data.get("meta", [])

print(f"\n{'='*60}")
print(f"TOTAL CHUNKS IN INDEX: {len(chunks)}")
print(f"{'='*60}\n")

# Search for story-related chunks
story_keywords = [
    "varalakshmi",
    "charumathi",
    "guru poornima",
    "vyasa",
    "diwali",
    "ram",
    "ayodhya",
    "lakshmi",
    "story",
    "significance"
]

print("SEARCHING FOR STORY CONTENT...\n")

story_chunks = []
for chunk in chunks:
    text_lower = chunk['text'].lower()
    source = chunk['source']
    
    # Check if this chunk contains story content
    if any(kw in text_lower for kw in story_keywords):
        story_chunks.append(chunk)

print(f"Found {len(story_chunks)} chunks with story-related content\n")

# Show chunks from story files
print("="*60)
print("CHUNKS FROM STORY FILES:")
print("="*60 + "\n")

story_files = [
    "Varalakshmi_Vratham",
    "Guru_Poornima", 
    "story_of_Diwali",
    "Mahalakshmi_Jayanthi",
    "Ramanujacharya_Jayanthi"
]

for story_file in story_files:
    matching = [c for c in chunks if story_file in c['source']]
    
    if matching:
        print(f"✅ {story_file}: {len(matching)} chunks")
        # Show first chunk preview
        if matching:
            preview = matching[0]['text'][:200] + "..."
            print(f"   Preview: {preview}\n")
    else:
        print(f"❌ {story_file}: NOT FOUND IN INDEX\n")

# Check specific story content
print("\n" + "="*60)
print("CHECKING FOR SPECIFIC STORY CONTENT:")
print("="*60 + "\n")

test_searches = [
    ("Charumathi story", "charumathi"),
    ("Vyasa contribution", "vyasa"),
    ("Ram Ayodhya return", "ayodhya"),
    ("Lakshmi incarnation", "incarnation")
]

for name, keyword in test_searches:
    matches = [c for c in chunks if keyword in c['text'].lower()]
    if matches:
        print(f"✅ {name}: Found in {len(matches)} chunks")
    else:
        print(f"❌ {name}: NOT FOUND")

print("\n" + "="*60)
print("RECOMMENDATIONS:")
print("="*60)

story_file_chunks = sum(1 for c in chunks if any(sf in c['source'] for sf in story_files))

if story_file_chunks == 0:
    print("""
❌ NO STORY FILES FOUND IN INDEX!

SOLUTION:
1. Verify files exist in data_raw/Rituals/:
   dir data_raw\\Rituals

2. If files exist, rebuild index:
   python build.py

3. Check build output for errors
""")
elif story_file_chunks < 10:
    print(f"""
⚠️  Only {story_file_chunks} chunks from story files found.

This might be too few. Story files should generate more chunks.

SOLUTION:
1. Check if files are being properly chunked
2. Look at build.py output when running
3. Verify chunk size limits aren't cutting off content
""")
else:
    print(f"""
✅ Good! {story_file_chunks} chunks from story files indexed.

If stories still not appearing in responses, the issue is likely:
1. Query expansion not working correctly
2. FAISS retrieval not ranking story chunks high enough
3. LLM prompt filtering out story content

Run test queries to diagnose:
   python test_queries.py
""")

print("="*60 + "\n")
