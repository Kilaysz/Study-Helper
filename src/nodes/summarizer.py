from src.utils.llm_setup import get_llm

def summarizer_node(state):
    """
    Summarizes the uploaded document.
    """
    llm = get_llm()
    file_content = state.get("file_content", "")
    
    if not file_content:
        return {"messages": ["⚠️ Please upload a document for me to summarize."]}
    
    # We limit content to avoid overflowing context window (approx 4000 chars)
    # For a production app, you'd use a Map-Reduce chain here for full docs.
    context = file_content[:4000]
    
    prompt = f"""
    You are an expert Study Assistant.
    
    Task: Provide a comprehensive summary of the following text.
    - Highlight the main arguments.
    - List key concepts and definitions.
    - Use bullet points for readability.
    
    Text:
    {context}
    """
    
    print("📝 Generating Summary...")
    response = llm.invoke(prompt)
    
    return {"messages": [response]}