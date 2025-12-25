from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import shutil
import os
import uvicorn
import traceback

# Internal Imports
from src.graph import build_graph
from src.utils.pdf_loader import load_pdf_content

# Load Environment
load_dotenv()

app = FastAPI(title="Study Partner Agent API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Graph
try:
    agent_app = build_graph()
    print("✅ LangGraph Agent initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize LangGraph: {e}")
    agent_app = None

# Models
class ChatRequest(BaseModel):
    message: str
    file_content: Optional[str] = None
    history: List[Dict[str, str]] = []

@app.get("/")
def read_root():
    return {"status": "Study Partner Agent is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles PDF uploads. Now only extracts text and returns it.
    """
    try:
        if os.path.exists("data"):
            shutil.rmtree("data")
        os.makedirs("data")
        file_path = f"data/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📂 File saved: {file_path}")
        
        # 1. Extract Text
        markdown_text = load_pdf_content(file_path)
        print(markdown_text[:500])  # Print first 500 chars for verification
        # REMOVED: index_document(markdown_text, file.filename)
        print("✅ Document text extracted (Vector Indexing Skipped).")
        
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
        print(f"📩 Processing Message: {request.message}")
        
        # Prepare LangGraph Inputs
        # Note: We do NOT pass 'mode' anymore. The 'classifier' node handles it.
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