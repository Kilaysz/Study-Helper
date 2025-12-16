from src.utils.llm_setup import get_llm
from src.tools import get_all_tools

def summarizer_node(state):
    """
    Summarizes the uploaded document.
    """
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    file_content = state.get("file_content", "")
    
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
    
    print("📝 Generating Summary...")
    response = llm.invoke(prompt)
    
    return {"messages": [response]}