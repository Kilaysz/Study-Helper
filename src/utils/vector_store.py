import os
import json
import shutil
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)
from langchain_core.documents import Document

# --- CONFIG ---
DB_PATH_USER = "./chroma_db_user"       # 🗑️ Ephemeral (User Docs)
DB_PATH_FACULTY = "./chroma_db_faculty" # 🔒 Permanent (Professors)

OLLAMA_URL = os.getenv("OLLAMA_LOCAL_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"

def get_embeddings():
    return OllamaEmbeddings(
        model=EMBED_MODEL,
        base_url=OLLAMA_URL
    )

# --- HELPER: Get Specific DB ---
def get_vector_store(db_type: str):
    """
    Returns the requested Vector Store instance.
    db_type: "user" or "faculty"
    """
    path = DB_PATH_USER if db_type == "user" else DB_PATH_FACULTY
    return Chroma(
        persist_directory=path,
        embedding_function=get_embeddings()
    )

# ==========================================
# 1. PROFESSOR INDEXING (Permanent DB)
# ==========================================

def index_professors_to_chroma():
    """
    Indexes professors into the DEDICATED Faculty DB.
    """
    json_path = "data/professors.json"
    if not os.path.exists(json_path):
        print("⚠️ No professors.json found. Skipping.")
        return

    # Check if Faculty DB already exists (to avoid re-indexing)
    if os.path.exists(DB_PATH_FACULTY) and os.listdir(DB_PATH_FACULTY):
        print("✅ Faculty Database already exists. Skipping re-index.")
        return

    print("📊 Building Faculty Database...")
    with open(json_path, "r", encoding="utf-8") as f:
        professors = json.load(f)

    splitter = TokenTextSplitter(chunk_size=256, chunk_overlap=32)
    docs = []

    for prof in professors:
        name = prof.get("name", "Unknown")
        lab = prof.get("lab", "N/A")
        areas = prof.get("areas", "N/A")
        raw_info = prof.get("raw_info", "")

        if not raw_info.strip(): continue

        chunks = splitter.split_text(raw_info)
        for chunk in chunks:
            content = f"Professor: {name}\nLab: {lab}\nAreas: {areas}\n\n{chunk}"
            docs.append(Document(
                page_content=content,
                metadata={"source": "faculty_db", "name": name}
            ))

    if docs:
        # Save to FACULTY path
        vector_store = Chroma(
            persist_directory=DB_PATH_FACULTY,
            embedding_function=get_embeddings()
        )
        # Batch add
        batch_size = 50
        for i in range(0, len(docs), batch_size):
            vector_store.add_documents(docs[i:i + batch_size])
        
        print(f"✅ Indexed {len(docs)} faculty chunks to {DB_PATH_FACULTY}")

# ==========================================
# 2. USER FILE INDEXING (Ephemeral DB)
# ==========================================

def index_document(text: str, filename: str):
    """
    Wipes the User DB and creates a fresh one for the new file.
    """
    print(f"🧹 Wiping old user database at {DB_PATH_USER}...")
    
    # HARD DELETE: Remove the folder entirely to ensure it's empty
    if os.path.exists(DB_PATH_USER):
        shutil.rmtree(DB_PATH_USER)
    
    # Re-create empty
    os.makedirs(DB_PATH_USER, exist_ok=True)

    print(f"📊 Indexing new file: {filename}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, add_start_index=True
    )
    
    chunks = splitter.create_documents(
        [text], metadatas=[{"source": filename}]
    )

    # Save to USER path
    vector_store = Chroma(
        persist_directory=DB_PATH_USER,
        embedding_function=get_embeddings()
    )
    vector_store.add_documents(chunks)
    print("✅ User document indexed successfully.")

# ==========================================
# 3. RETRIEVING (Targeted)
# ==========================================

def get_retriever(k: int = 5, db_type: str = "user"):
    """
    Get a retriever for a SPECIFIC database.
    db_type: 'user' (default) or 'faculty'
    """
    path = DB_PATH_FACULTY if db_type == "faculty" else DB_PATH_USER
    
    # Check if DB exists before trying to load it
    if not os.path.exists(path) or not os.listdir(path):
        # Return an empty retriever or handle gracefully if DB is missing
        # We create a dummy empty store just to avoid crashing
        return Chroma(
            persist_directory=path, 
            embedding_function=get_embeddings()
        ).as_retriever(search_kwargs={"k": 1})

    vector_store = Chroma(
        persist_directory=path,
        embedding_function=get_embeddings()
    )
    
    return vector_store.as_retriever(search_kwargs={"k": k})