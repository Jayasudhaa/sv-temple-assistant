#!/usr/bin/env python3
"""
Test script to verify FAISS improvements for temple chatbot
Run this after rebuilding the index with build_improved.py
"""

import sys
import json
from pathlib import Path

# Test queries that should work after fixes
TEST_QUERIES = [
    # Abhishekam queries
    {
        "query": "when is hanuman abhishekam",
        "should_contain": ["hanuman", "saturday", "4th"],
        "description": "Hanuman abhishekam schedule"
    },
    {
        "query": "when is shiva abhishekam",
        "should_contain": ["shiva", "siva", "sunday"],
        "description": "Shiva abhishekam schedule"
    },
    {
        "query": "ganapathi abhishekam schedule",
        "should_contain": ["ganapathi", "ganesh", "sunday", "2nd"],
        "description": "Ganapathi abhishekam schedule"
    },
    
    # Event queries
    {
        "query": "when is karthika deepam",
        "should_contain": ["karthika deepam", "december", "full moon"],
        "description": "December event"
    },
    {
        "query": "what events in november",
        "should_contain": ["november", "tulasi", "karthika"],
        "description": "November events"
    },
    {
        "query": "when is vaikunta ekadasi",
        "should_contain": ["vaikunta ekadasi", "december", "30"],
        "description": "Major December event"
    },
    
    # Date queries
    {
        "query": "when is full moon in december",
        "should_contain": ["december", "purnima", "full moon"],
        "description": "December full moon"
    },
]


def test_chunking():
    """Verify chunks are properly formed"""
    print("\n" + "="*60)
    print("STEP 1: VERIFYING CHUNK QUALITY")
    print("="*60)
    
    meta_file = Path("backend/faiss_store/meta.json")
    
    if not meta_file.exists():
        print("❌ ERROR: meta.json not found!")
        print("   Run: python build.py first")
        return False
    
    with open(meta_file) as f:
        data = json.load(f)
    
    chunks = data.get("meta", [])
    print(f"\n✅ Found {len(chunks)} total chunks")
    
    # Check for proper event chunks
    event_chunks = [c for c in chunks if "event" in c["source"].lower()]
    print(f"✅ Event chunks: {len(event_chunks)}")
    
    # Check for proper abhishekam chunks
    abhi_chunks = [c for c in chunks if "abhishekam" in c["source"].lower()]
    print(f"✅ Abhishekam chunks: {len(abhi_chunks)}")
    
    # Sample chunks
    print("\n📋 Sample chunks (showing first 200 chars):")
    for i, chunk in enumerate(chunks[:3], 1):
        text = chunk["text"]
        preview = text[:200] + "..." if len(text) > 200 else text
        print(f"\nChunk {i} ({Path(chunk['source']).name}):")
        print(f"  {preview}")
        
        # Check if it's a complete unit (not fragmented)
        if "\n" in text and len(text) > 100:
            print(f"  ✅ Multi-line chunk (good!)")
        elif len(text) < 50:
            print(f"  ⚠️  Very short chunk - might be fragmented")
    
    return True


def test_retrieval():
    """Test retrieval with actual queries"""
    print("\n" + "="*60)
    print("STEP 2: TESTING RETRIEVAL")
    print("="*60)
    
    try:
        # Import the improved retrieval
        sys.path.insert(0, str(Path.cwd()))
        from retrieval_improved import get_chunks
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(TEST_QUERIES, 1):
            print(f"\n--- Test {i}/{len(TEST_QUERIES)}: {test['description']} ---")
            print(f"Query: \"{test['query']}\"")
            
            try:
                chunks = get_chunks(test['query'], k=5)
                
                if not chunks:
                    print(f"❌ FAIL: No chunks retrieved")
                    failed += 1
                    continue
                
                # Combine all retrieved text
                all_text = " ".join([c["text"] for c in chunks]).lower()
                
                # Check if expected keywords present
                found_keywords = [kw for kw in test['should_contain'] if kw.lower() in all_text]
                missing_keywords = [kw for kw in test['should_contain'] if kw.lower() not in all_text]
                
                if len(found_keywords) >= len(test['should_contain']) * 0.6:  # 60% threshold
                    print(f"✅ PASS: Found {len(found_keywords)}/{len(test['should_contain'])} keywords")
                    print(f"   Keywords found: {found_keywords}")
                    passed += 1
                else:
                    print(f"❌ FAIL: Only found {len(found_keywords)}/{len(test['should_contain'])} keywords")
                    print(f"   Found: {found_keywords}")
                    print(f"   Missing: {missing_keywords}")
                    failed += 1
                
                # Show top result
                print(f"\n   Top result preview:")
                preview = chunks[0]["text"][:150] + "..." if len(chunks[0]["text"]) > 150 else chunks[0]["text"]
                print(f"   {preview}")
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                failed += 1
        
        print("\n" + "="*60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("="*60)
        
        return failed == 0
        
    except ImportError as e:
        print(f"❌ ERROR: Could not import retrieval module")
        print(f"   {e}")
        print("\n   Make sure you've copied retrieval_improved.py to the right location")
        return False


def test_integration():
    """Test full integration with ask_temple.py"""
    print("\n" + "="*60)
    print("STEP 3: TESTING FULL INTEGRATION (Optional)")
    print("="*60)
    
    try:
        sys.path.insert(0, str(Path.cwd() / "backend"))
        from ask_temple import answer_user
        
        test_queries = [
            "when is hanuman abhishekam",
            "what events in december",
            "when is full moon"
        ]
        
        print("\nTesting with actual chatbot responses:")
        for query in test_queries:
            print(f"\n📱 User: {query}")
            response = answer_user(query, user_id="test_user")
            print(f"🤖 Bot: {response[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"⚠️  Integration test skipped: {e}")
        print("   This is OK - the main retrieval tests are what matter")
        return True


def main():
    """Run all tests"""
    print("\n" + "🕉"*20)
    print("  SRI VENKATESWARA TEMPLE CHATBOT - FAISS TEST SUITE")
    print("🕉"*20)
    
    # Check if index exists
    if not Path("backend/faiss_store/index.faiss").exists():
        print("\n❌ ERROR: FAISS index not found!")
        print("\n📝 Please run these steps first:")
        print("   1. Copy build_improved.py to build.py")
        print("   2. Run: python build.py")
        print("   3. Run this test again")
        return
    
    all_passed = True
    
    # Test 1: Chunking
    if not test_chunking():
        all_passed = False
    
    # Test 2: Retrieval
    if not test_retrieval():
        all_passed = False
    
    # Test 3: Integration (optional)
    test_integration()
    
    # Final summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYour FAISS index is working correctly.")
        print("You can now deploy to Lambda.")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the failed tests above.")
        print("Common fixes:")
        print("  1. Make sure you rebuilt the index: python build.py")
        print("  2. Check that data_raw/ has all your .txt files")
        print("  3. Verify Bedrock credentials are configured")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
