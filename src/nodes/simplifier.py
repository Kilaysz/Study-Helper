from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools
from src.utils.vector_store import get_retriever

def feynman_node(state):
    """
    Explains complex topics simply using the Feynman Technique.
    Uses search tools to verify facts before explaining.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # --- 1. RAG Retrieval Logic ---
    print(f"⚛️ Feynman Agent: Retrieving context for '{user_input}'...")
    context_content = ""
    
    try:
        retriever = get_retriever(k=1000, db_type="user")
        relevant_docs = retriever.invoke(user_input)
        
        if relevant_docs:
            context_content = "\n\n".join([doc.page_content for doc in relevant_docs])
            print(f"   ✅ Found {len(relevant_docs)} relevant chunks.")
            
    except Exception as e:
        print(f"   ⚠️ Retrieval skipped/failed: {e}")

    # Fallback: If retrieval found nothing, use the raw file from state
    if not context_content:
        raw_file = state.get("file_content", "") or ""
        context_content = raw_file[:30000] # Safe fallback limit
        if raw_file:
            print("   ⚠️ Using raw file fallback.")
        else:
            print("   ⚠️ No context available.")

    # --- 2. Bind Tools ---
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # --- 3. Construct Prompt ---
    system_prompt = f"""
    You are Richard Feynman, the famous physicist known for simple explanations.
    
    ### CONTEXT (Reference Material)
    {context_content}
    
    ### USER REQUEST
    "{user_input}"
    
    ### TASK
    1. **Check Facts:** If the user asks for outside info not in the Context, USE THE SEARCH TOOL immediately.
    2. **Explain:** Once you have the info, explain the concept in simple, plain English.
    3. **Analogy:** You MUST use a real-world analogy (e.g., "Imagine a water pipe..." or "Think of it like a library...").
    4. **Tone:** Curious, direct, and slightly informal. Avoid academic jargon.
    5. **Citations:** If you use the search tool, cite your source.
    """
    
    # Use SystemMessage to properly set the AI's persona
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    print("💡 Feynman Agent: Thinking (and possibly searching)...")
    
    # --- 4. Invoke with Tools ---
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}