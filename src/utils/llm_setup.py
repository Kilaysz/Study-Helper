import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

# 1. Robustly load .env from the project root
# This finds the file: current_folder/../../.env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

def get_llm():
    """
    Returns the standard LangChain ChatOllama instance.
    This automatically has .invoke(), .stream(), and .batch() methods.
    """
    # 2. Get Config
    base_url = os.getenv("OLLAMA_BASE_URL")
    api_key = os.getenv("OLLAMA_API_KEY")
    model = os.getenv("OLLAMA_MODEL")

    # Debugging: See what is actually being loaded
    if not base_url:
        print("⚠️  WARNING: OLLAMA_BASE_URL not found in .env. Defaulting to localhost.")
    else:
        print(f"🔌 LLM Setup: Connecting to {base_url} (Model: {model})")
    
    # 4. Prepare Headers
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # 5. Instantiate the Built-in Class
    llm = ChatOllama(
        model=model,
        base_url=base_url,
        headers=headers, # This passes your key to the server
        temperature=0.7
    )
    
    return llm