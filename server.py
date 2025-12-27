import os
import shutil
import traceback
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- INTERNAL IMPORTS ---
from src.graph import build_graph
from src.utils.pdf_loader import load_pdf_content
from src.utils.vector_store import index_document, index_professors_to_chroma
from src.utils.scrape_professor import scrape_ncku_professors

# Load Environment
load_dotenv()

# Global Agent Variable
agent_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executes on Server Startup.
    1. Initializes the AI Graph.
    2. Checks if Professor data exists. If not, Scrapes and Indexes it.
    """
    global agent_app
    
    print("🔄 Server Startup Sequence Initiated...")

    # 1. Initialize LangGraph
    try:
        agent_app = build_graph()
        print("   ✅ LangGraph Agent initialized.")
    except Exception as e:
        print(f"   ❌ Failed to initialize LangGraph: {e}")

    # 2. Professor Database Check
    # We use 'data/' for persistent system data (Professors)
    os.makedirs("data", exist_ok=True) 
    json_path = "data/professors.json"
    
    if not os.path.exists(json_path):
        print("   🚀 First run detected! Building Professor Database...")
        
        # A. Run Scraper
        print("      🕷️ Step 1: Scraping NCKU Website...")
        scrape_ncku_professors() 
        
        # B. Run Indexer
        print("      📊 Step 2: Indexing to Vector Store...")
        index_professors_to_chroma()
        
        print("   ✅ Professor DB Ready.")
    else:
        print("   ✅ Professor Database found. Skipping scrape.")

    # 3. Ensure Upload Directory Exists
    # We use 'uploads/' for temporary user files
    os.makedirs("uploads", exist_ok=True)
    
    yield
    # (Shutdown logic can go here if needed)


# --- APP SETUP ---
app = FastAPI(title="Study Partner Agent API", lifespan=lifespan)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    file_content: Optional[str] = None
    history: List[Dict[str, str]] = []

@app.get("/")
def read_root():
    return {"status": "Study Partner Agent is running"}


@app.delete("/delete-file")
async def delete_file():
    """
    Clears the uploaded USER file (Ephemeral).
    SAFE: Only deletes 'uploads/', leaves 'data/' (professors) alone.
    """
    try:
        if os.path.exists("uploads"):
            shutil.rmtree("uploads")
            print("🗑️ Deleted 'uploads' directory (User Context Cleanup).")
        
        # Recreate empty folder
        os.makedirs("uploads", exist_ok=True)
        
        return {"status": "success", "message": "User context cleared."}
    except Exception as e:
        print(f"❌ Delete Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles PDF uploads. Saves to 'uploads/' directory.
    """
    try:
        # 1. Prepare Directory (Single File Mode)
        # We wipe 'uploads' to ensure only one active file, but keep 'data' safe
        if os.path.exists("uploads"):
            shutil.rmtree("uploads")
        os.makedirs("uploads")
        
        file_path = f"uploads/{file.filename}" # <--- Saving to uploads/
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📂 User File saved: {file_path}")
        
        # 2. Extract Text
        markdown_text = load_pdf_content(file_path)
        print(markdown_text[:500])

        try:
            index_document(markdown_text, file.filename)
            print("✅ Document Indexed to Vector Store.")
        except Exception as e:
            print(f"⚠️ Vector Indexing Warning: {e}")

        return {
            "filename": file.filename, 
            "content": markdown_text,
            "status": "success"
        }
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not agent_app:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        print(f"📩 Processing Message: {request.message[:50]}...")
        
        # Prepare LangGraph Inputs
        current_messages = request.history + [{"role": "user", "content": request.message}]
        
        inputs = {
            "messages": current_messages,
            "file_content": request.file_content
        }
        
        # Run the Graph
        result = agent_app.invoke(inputs)
        
        # Get Response
        last_message = result["messages"][-1]
        
        return {"response": last_message.content}
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ CHAT ERROR:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Server on http://0.0.0.0:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)