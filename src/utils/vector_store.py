import os
import json
import shutil
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

# --- SINGLETON STORAGE ---
# We store instances here: {'user': ChromaObj, 'faculty': ChromaObj}
# This prevents opening multiple connections to the same folder (WinError 32 fix)
_active_dbs = {} 

def get_embeddings():
    return OllamaEmbeddings(
        model=EMBED_MODEL,
        base_url=OLLAMA_URL
    )

def get_vector_store(db_type: str):
    """
    The Single Source of Truth for DB connections.
    db_type: "user" or "faculty"
    """
    global _active_dbs
    
    # 1. Determine Path & Collection Name
    if db_type == "user":
        path = DB_PATH_USER
        collection = "user_rag_collection"
    elif db_type == "faculty":
        path = DB_PATH_FACULTY
        collection = "faculty_rag_collection"
    else:
        raise ValueError("Invalid db_type. Use 'user' or 'faculty'.")

    # 2. Return existing instance if available (Singleton)
    if db_type in _active_dbs:
        return _active_dbs[db_type]

    # 3. Create new ONLY if missing
    print(f"🔌 Establishing connection to {db_type} ChromaDB...")
    instance = Chroma(
        persist_directory=path,
        embedding_function=get_embeddings(),
        collection_name=collection
    )
    
    _active_dbs[db_type] = instance
    return instance

# ==========================================
# 1. USER DB MANAGEMENT (Ephemeral)
# ==========================================

def clear_database():
    """
    Clears the User DB by deleting content, NOT the folder.
    This is safe for Windows file locks.
    """
    try:
        # Use the singleton getter
        db = get_vector_store("user")
        
        # Get all IDs currently in the DB
        existing_data = db.get()
        ids_to_delete = existing_data['ids']
        
        if ids_to_delete:
            print(f"🗑️ Deleting {len(ids_to_delete)} existing user documents...")
            db.delete(ids_to_delete)
            print("✅ User Database content wiped.")
        else:
            print("ℹ️ User Database was already empty.")
            
        return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def index_document(text: str, filename: str):
    """
    1. Wipes old User DB content (Safely).
    2. Indexes new file content.
    """
    # Step 1: Clear old data safely
    clear_database()

    # Step 2: Prepare new chunks
    print(f"📊 Indexing new file: {filename}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100, add_start_index=True
    )
    chunks = splitter.create_documents(
        [text], metadatas=[{"source": filename}]
    )

    # Step 3: Add to DB (using Singleton)
    db = get_vector_store("user")
    db.add_documents(chunks)
    print("✅ User document indexed successfully.")

# ==========================================
# 2. FACULTY DB MANAGEMENT (Permanent)
# ==========================================

def index_professors_to_chroma():
    """
    Indexes professors into the Faculty DB if it's empty.
    """
    json_path = "data/professors.json"
    if not os.path.exists(json_path):
        print("⚠️ No professors.json found. Skipping.")
        return

    # Use Singleton to check existence
    db = get_vector_store("faculty")
    existing = db.get()
    
    # If we have IDs, the DB is already built. Skip.
    if existing['ids']:
        print("✅ Faculty Database already populated. Skipping re-index.")
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
        print(f"📥 Adding {len(docs)} faculty chunks...")
        # Add in batches to be safe
        batch_size = 50
        for i in range(0, len(docs), batch_size):
            db.add_documents(docs[i:i + batch_size])
        
        print(f"✅ Indexed all faculty to {DB_PATH_FACULTY}")

# ==========================================
# 3. RETRIEVER ACCESS
# ==========================================

def get_retriever(k: int = 5, db_type: str = "user"):
    """
    Returns retriever from the cached Singleton instance.
    """
    db = get_vector_store(db_type)
    return db.as_retriever(search_kwargs={"k": k})