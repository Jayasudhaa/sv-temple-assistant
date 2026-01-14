import os
import json
from pathlib import Path
import boto3
import numpy as np
import faiss

DATA_DIR = Path("data_raw")
FAISS_DIR = Path("backend/faiss_store")
FAISS_DIR.mkdir(parents=True, exist_ok=True)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# ============================================================
# IMPROVED CHUNKING STRATEGY
# ============================================================

def split_large_chunk(text, max_size=2000):
    """
    Split a large chunk into smaller pieces while preserving meaning
    """
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    
    # Try splitting by double newlines (paragraphs) first
    paragraphs = text.split("\n\n")
    
    current_chunk = ""
    for para in paragraphs:
        # If adding this paragraph would exceed limit
        if len(current_chunk) + len(para) + 2 > max_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # If we still have oversized chunks, split by single newlines
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_size:
            final_chunks.append(chunk)
        else:
            # Split by lines
            lines = chunk.split("\n")
            current = ""
            for line in lines:
                if len(current) + len(line) + 1 > max_size:
                    if current:
                        final_chunks.append(current.strip())
                    current = line
                else:
                    if current:
                        current += "\n" + line
                    else:
                        current = line
            if current:
                final_chunks.append(current.strip())
    
    return final_chunks


def smart_chunk_events(text, source_file):
    """
    Smart chunking for event files - keeps related information together
    Max chunk size: 2000 chars (Cohere limit is 2048)
    """
    MAX_CHUNK_SIZE = 2000
    chunks = []
    
    # Events are separated by lines of "═══..." or blank lines
    sections = []
    current_section = []
    
    lines = text.split("\n")
    
    for line in lines:
        # Separator line (═══) marks section boundary
        if line.strip().startswith("═"):
            if current_section:
                # Join the section and save it
                section_text = "\n".join(current_section).strip()
                if section_text and len(section_text) > 30:
                    sections.append(section_text)
                current_section = []
        else:
            if line.strip():  # Non-empty line
                current_section.append(line)
    
    # Don't forget last section
    if current_section:
        section_text = "\n".join(current_section).strip()
        if section_text and len(section_text) > 30:
            sections.append(section_text)
    
    # Split oversized sections
    final_chunks = []
    for section in sections:
        if len(section) <= MAX_CHUNK_SIZE:
            final_chunks.append(section)
        else:
            # Split large section by paragraphs/lines
            sub_chunks = split_large_chunk(section, MAX_CHUNK_SIZE)
            final_chunks.extend(sub_chunks)
    
    return final_chunks


def smart_chunk_abhishekam(text, source_file):
    """
    Smart chunking for abhishekam schedule - keeps deity schedules together
    Max chunk size: 2000 chars
    """
    MAX_CHUNK_SIZE = 2000
    chunks = []
    
    # Split by section separators or TYPE headers
    sections = []
    current_section = []
    
    lines = text.split("\n")
    
    for i, line in enumerate(lines):
        # Section separator or major header
        if line.strip().startswith("═") or line.strip().startswith("TYPE"):
            if current_section:
                section_text = "\n".join(current_section).strip()
                if section_text and len(section_text) > 30:
                    sections.append(section_text)
                current_section = []
            
            # Start new section with header
            if line.strip().startswith("TYPE"):
                current_section.append(line)
        else:
            if line.strip():
                current_section.append(line)
    
    # Last section
    if current_section:
        section_text = "\n".join(current_section).strip()
        if section_text and len(section_text) > 30:
            sections.append(section_text)
    
    # Also create individual entries for monthly schedule items
    # Extract lines like "1st Saturday - Sri Venkateswara Swamy (Moola Murthy): $151"
    for line in lines:
        if re.match(r'^\d+(st|nd|rd|th)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', line):
            # This is a schedule line - create a standalone chunk
            schedule_chunk = f"TEMPLE SCHEDULED ABHISHEKAM:\n{line.strip()}"
            if len(schedule_chunk) <= MAX_CHUNK_SIZE:
                sections.append(schedule_chunk)
    
    # Split oversized sections
    final_chunks = []
    for section in sections:
        if len(section) <= MAX_CHUNK_SIZE:
            final_chunks.append(section)
        else:
            sub_chunks = split_large_chunk(section, MAX_CHUNK_SIZE)
            final_chunks.extend(sub_chunks)
    
    return final_chunks


def smart_chunk_generic(text, source_file):
    """
    Generic chunking for other files - paragraph-based
    Max chunk size: 2000 chars
    """
    MAX_CHUNK_SIZE = 2000
    chunks = []
    
    # Split by double newlines (paragraphs)
    paragraphs = text.split("\n\n")
    
    for para in paragraphs:
        para = para.strip()
        if len(para) > MAX_CHUNK_SIZE:
            # Split large paragraph
            sub_chunks = split_large_chunk(para, MAX_CHUNK_SIZE)
            chunks.extend(sub_chunks)
        elif len(para) > 50:  # Minimum chunk size
            chunks.append(para)
        elif len(para) > 20:
            # Small paragraphs - try to combine with context
            chunks.append(para)
    
    return chunks


def load_all_text_chunks():
    """
    Load and intelligently chunk ALL .txt files
    """
    chunks = []
    sources = []
    
    for file in DATA_DIR.rglob("*.txt"):
        text = file.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            continue
        
        filename = file.name.lower()
        
        # Apply different chunking strategies based on file type
        if "event" in filename or "festival" in filename:
            file_chunks = smart_chunk_events(text, str(file))
        elif "abhishekam" in filename:
            file_chunks = smart_chunk_abhishekam(text, str(file))
        else:
            file_chunks = smart_chunk_generic(text, str(file))
        
        # Add chunks with source tracking
        for chunk in file_chunks:
            if chunk and len(chunk) > 20:
                chunks.append(chunk)
                sources.append(str(file))
    
    return chunks, sources


# ---------- EMBEDDINGS (UNCHANGED) -------------
def embed_bedrock(text_list):
    body = {
        "texts": text_list,
        "input_type": "search_document"
    }

    resp = bedrock.invoke_model(
        modelId="cohere.embed-english-v3",
        body=json.dumps(body),
        contentType="application/json"
    )

    data = json.loads(resp["body"].read())
    return data["embeddings"]


# ---------- BUILD INDEX -------------
def build_index():
    print("Loading and chunking text with IMPROVED strategy...")
    chunks, sources = load_all_text_chunks()
    print(f"Total chunks: {len(chunks)}")

    if len(chunks) == 0:
        raise Exception("❌ No chunks found! Check your data_raw/ folder structure.")

    # Validate chunk sizes
    MAX_CHUNK_SIZE = 2000
    oversized = []
    for i, chunk in enumerate(chunks):
        if len(chunk) > MAX_CHUNK_SIZE:
            oversized.append((i, len(chunk), sources[i]))
    
    if oversized:
        print(f"\n⚠️  WARNING: Found {len(oversized)} oversized chunks:")
        for idx, size, source in oversized[:5]:  # Show first 5
            print(f"   Chunk {idx}: {size} chars from {source}")
        print(f"\n   Truncating oversized chunks to {MAX_CHUNK_SIZE} chars...")
        
        # Truncate oversized chunks
        for idx, size, source in oversized:
            chunks[idx] = chunks[idx][:MAX_CHUNK_SIZE]

    # Show sample chunks for verification
    print("\n📋 Sample chunks (first 3):")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ({sources[i]}) ---")
        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)

    # Embed in batches
    vectors = []
    batch_size = 32

    print("\nEmbedding chunks with Bedrock...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        # Double-check batch sizes before sending
        for j, text in enumerate(batch):
            if len(text) > 2048:
                print(f"⚠️  Truncating chunk {i+j} from {len(text)} to 2048 chars")
                batch[j] = text[:2000]
        
        embeds = embed_bedrock(batch)
        vectors.extend(embeds)
        print(f"Embedded {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

    vectors = np.array(vectors, dtype="float32")
    dim = vectors.shape[1]

    # FAISS index
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    print("\nSaving FAISS index...")
    faiss.write_index(index, str(FAISS_DIR / "index.faiss"))

    print("Saving metadata...")
    meta = []
    for i, text in enumerate(chunks):
        meta.append({"id": i, "source": sources[i], "text": text})

    with open(FAISS_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta}, f, indent=2)

    print("🎉 DONE – FAISS index built successfully!")
    print(f"📊 Total vectors: {len(vectors)}, Dimension: {dim}")


if __name__ == "__main__":
    import re  # Import for regex in abhishekam chunking
    build_index()