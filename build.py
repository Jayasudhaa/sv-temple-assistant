# build_tiny.py — READS .txt AND .pdf FROM data_raw/
import os, json, faiss
from backend.embeddings import embed

# PDF SUPPORT
try:
    import PyPDF2
    HAS_PDF = True
    print("PyPDF2 loaded — PDF support ON")
except:
    HAS_PDF = False
    print("PyPDF2 not found — PDF support OFF (run: pip install PyPDF2)")

INPUT = "data_raw"
OUT = "backend/faiss_store"
os.makedirs(OUT, exist_ok=True)

texts = []
meta = []

print("Scanning data_raw for .txt and .pdf files...")
for file in sorted(os.listdir(INPUT)):
    path = os.path.join(INPUT, file)
    raw = ""

    # --- READ .txt ---
    if file.lower().endswith(".txt"):
        raw = open(path, "r", encoding="utf-8").read()

    # --- READ .pdf ---
    elif file.lower().endswith(".pdf") and HAS_PDF:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                raw = "\n".join(page.extract_text() or "" for page in reader.pages)
            print(f"Extracted {len(raw)} chars from PDF: {file}")
        except Exception as e:
            print(f"PDF error {file}: {e}")
            continue

    if not raw.strip():
        continue

    # --- CHUNK TEXT (500-char chunks) ---
    chunks = [raw[i:i+600] for i in range(0, len(raw), 500)]
    for i, c in enumerate(chunks):
        texts.append(c)
        meta.append({
            "source": file,
            "chunk_id": i,
            "text": c
        })

print(f"Found {len(texts)} chunks from {len([f for f in os.listdir(INPUT) if f.endswith(('.txt','.pdf'))])} files")

# --- EMBED ---
print("Embedding...")
vecs = embed(texts)

# --- BUILD FAISS ---
print("Building FAISS index...")
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

# --- SAVE ---
print("Saving index.faiss + meta.json...")
faiss.write_index(index, os.path.join(OUT, "index.faiss"))
json.dump({"meta": meta}, open(os.path.join(OUT, "meta.json"), "w"), indent=2)

print("DONE! meta.json updated with ALL .txt and .pdf files.")
print("Run: Compress-Archive -Path app.py,requirements.txt,backend,data_raw -DestinationPath BOT.zip -Force")