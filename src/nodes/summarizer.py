import os
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools
from src.utils.pdf_loader import load_pdf_content

def summarizer_node(state):
    """
    Summarizes the uploaded document.
    """
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    file_name = state.get("file_name", "")
    
    file_content = ""
    if file_name:
        file_path = f"{file_name}"  # Reconstruct the path used in server.py
        if os.path.exists(file_path):
            file_content = load_pdf_content(file_path)
        else:
            file_content = "Error: File not found on server."

    prompt = f"""
    You are an expert Study Assistant.
    
    Task: Provide a comprehensive summary of the following text.
    - Highlight the main arguments.
    - List key concepts and definitions.
    - Use bullet points for readability.
    
    File:
    {file_content}

    ️Text:
    {state['messages'][-1].content}
    """
    message = [prompt] + state["messages"]
    print("📝 Generating Summary...")
    response = llm.invoke(message)
    
    return {"messages": [response]}