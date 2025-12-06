from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import os
import uvicorn

# --- INTERNAL IMPORTS ---
# Ensure your 'src' folder has an __init__.py file so these work
from src.graph import build_graph
from src.utils.pdf_loader import load_pdf_content

# --- APP SETUP ---
app = FastAPI(title="Study Partner Agent API")

# Configure CORS to allow your React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # In production, replace with ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Agent Graph ONCE when the server starts
# This compiles the graph and prepares it for requests
try:
    agent_app = build_graph()
    print("✅ LangGraph Agent initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize LangGraph: {e}")
    agent_app = None

# --- DATA MODELS ---
class ChatRequest(BaseModel):
    message: str
    file_content: Optional[str] = None
    # We default to "auto" so the Router Node can decide
    mode: Optional[str] = "auto" 
    # History comes in as a list of {role: str, content: str}
    history: List[Dict[str, str]] = []

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "Study Partner Agent is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles PDF uploads.
    1. Saves the file to a temporary 'data/' folder.
    2. Uses 'pdf_loader.py' to convert it to text.
    3. Returns the text to the Frontend.
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        file_path = f"data/{file.filename}"
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📂 File saved: {file_path}")
        
        # Extract text
        markdown_text = load_pdf_content(file_path)
        
        return {
            "filename": file.filename, 
            "content": markdown_text,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    The main Agent Loop.
    1. Constructs the state from the React request.
    2. Invokes the LangGraph agent.
    3. Returns the final response.
    """
    if not agent_app:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    try:
        # 1. Prepare the Input State
        # We append the latest user message to the history
        current_messages = request.history + [{"role": "user", "content": request.message}]
        
        inputs = {
            "messages": current_messages,
            "file_content": request.file_content,
            "mode": request.mode or "auto"
        }
        
        print(f"🤖 Agent invoked with mode: {inputs['mode']}")
        
        # 2. Run the Agent
        # .invoke() runs the graph until it hits the END node
        result = agent_app.invoke(inputs)
        
        # 3. Extract Response
        # The result state contains the full list of messages. We want the last one.
        last_message = result["messages"][-1]
        response_text = last_message.content
        
        return {"response": response_text}
        
    except Exception as e:
        print(f"❌ Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ENTRY POINT ---
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)