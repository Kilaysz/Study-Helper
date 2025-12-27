from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever  # <--- Import your Vector logic

def summarizer_node(state):
    """
    Summarizes the document using Vector Store (RAG) to handle large files.
    """
    llm = get_llm()
    user_query = state["messages"][-1].content
    
    # --- 1. RAG Retrieval (The Fix) ---
    print(f"📝 Summarizer: Retrieving chunks for: '{user_query}'...")
    
    # Request MORE chunks (k=10) for a summary than a quiz, 
    # so the model gets enough context (approx 5,000-10,000 chars).
    try:
        retriever = get_retriever(k=10, db_type="user")
        relevant_docs = retriever.invoke(user_query)
        context_content = "\n\n".join([doc for doc in relevant_docs if doc.metadata.get("source") == "user_upload"])
    except Exception as e:
        print(f"⚠️ Retrieval failed: {e}")
        context_content = ""

    # --- 2. Fallback Logic ---
    # If the vector store finds nothing (or isn't ready), 
    # fall back to the raw text from state, but TRUNCATE it safely (e.g., 15k chars).
    if not context_content:
        print("⚠️ Context empty, using raw fallback.")
        context_content = state.get("file_content", "")[:15000]

    # --- 3. Prompt Construction ---
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