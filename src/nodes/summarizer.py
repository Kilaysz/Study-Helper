from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever  # <--- Import your Vector logic

def summarizer_node(state):
    """
    Summarizes the document using Vector Store (RAG) to handle large files.
    """
    llm = get_llm()
    user_query = state["messages"][-1].content
    
    context_content = state.get("file_content", "")[:200000]

    # We put the text into a SystemMessage for better instruction following.
    system_prompt = f"""
    You are an expert Study Assistant.
    
    ### CONTEXT (Retrieved from Document)
    {context_content}
    
    ### INSTRUCTIONS
    Provide a comprehensive summary based on the context above.
    - Highlight the main arguments.
    - List key concepts and definitions.
    - Use bullet points for readability.
    - If the context is unrelated to the request, mention that.
    """

    # Combine System Prompt + User History
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    print("📝 Generating Summary...")
    response = llm.invoke(messages)
    
    return {"messages": [response]}