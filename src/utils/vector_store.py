import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Global variable to hold the database instance in memory
_vector_store = None

def get_embeddings():
    """Configures the Embedding Model (Ollama)"""
    return OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

def init_vector_store():
    """Initializes (or resets) the Vector DB"""
    global _vector_store
    # We use an in-memory vector store for simplicity in this study app.
    # For persistence, you would add `persist_directory="./chroma_db"`
    _vector_store = Chroma(
        collection_name="study_materials",
        embedding_function=get_embeddings()
    )
    return _vector_store

def index_document(text: str, filename: str):
    """
    1. Chunks the text.
    2. Embeds the chunks.
    3. Stores them in the Vector DB.
    """
    global _vector_store
    
    # 1. Reset/Init DB for the new file (assuming single-file focus)
    _vector_store = init_vector_store()
    
    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = text_splitter.create_documents(
        texts=[text], 
        metadatas=[{"source": filename}]
    )
    
    # 3. Index
    print(f"🗂️ Indexing {len(chunks)} chunks into Vector DB...")
    _vector_store.add_documents(chunks)
    print("✅ Indexing Complete.")

def get_retriever():
    """Returns the retriever interface for the Graph to use"""
    if _vector_store is None:
        return None
    return _vector_store.as_retriever()