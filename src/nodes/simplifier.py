from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools
from src.utils.vector_store import get_retriever

def feynman_node(state):
    """
    Explains complex topics simply using the Feynman Technique.
    Leverages pre-calculated chunk counts from State for efficient retrieval.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # --- 1. Intelligent Context Retrieval ---
    print(f"⚛️ Feynman Agent: Analyzing request: '{user_input}'...")
    context_content = ""
    
    try:
        # A. READ FROM STATE (Fast! No DB lookup needed)
        # server.py already injected 'chunk_count' into the state.
        total_chunks = state.get("chunk_count", 0)
        
        # B. Safety Cap (Max 50 chunks)
        # 50 chunks * ~500 chars = ~25,000 chars. 
        # This keeps us safely within Llama3's context window.
        safe_k = total_chunks
        
        if safe_k > 0:
            print(f"   📊 State indicates {total_chunks} total chunks. Fetching {safe_k}...")
            
            # Use the precise K value
            retriever = get_retriever(k=safe_k, db_type="user")
            relevant_docs = retriever.invoke(user_input)
            
            if relevant_docs:
                context_content = "\n\n".join([doc.page_content for doc in relevant_docs])
                print(f"   ✅ Successfully loaded context from {len(relevant_docs)} chunks.")
        else:
            print("   ℹ️ State indicates 0 chunks (or no file). Skipping vector search.")

    except Exception as e:
        print(f"   ⚠️ Retrieval logic skipped/failed: {e}")

    # --- 2. Fallback: Raw File Content ---
    if not context_content:
        raw_file = state.get("file_content", "") or ""
        
        # CRITICAL SAFETY LIMIT: 
        # 200,000 chars is too big. We limit to 30,000 (approx 8k tokens).
        safe_limit = 30000 
        
        if len(raw_file) > safe_limit:
            print(f"   ⚠️ Raw file is huge. Truncating to first {safe_limit} chars.")
            context_content = raw_file[:safe_limit]
        else:
            context_content = raw_file
            
        if context_content:
            print("   ⚠️ Using raw file content as fallback.")
        else:
            print("   ⚠️ No context available (File and DB empty).")

    # --- 3. Bind Tools ---
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # --- 4. Construct Feynman Prompt ---
    system_prompt = f"""
    You are Richard Feynman, the famous physicist known for explaining complex ideas simply.
    
    ### CONTEXT (Source Material)
    {context_content}
    
    ### USER REQUEST
    "{user_input}"
    
    ### YOUR INSTRUCTIONS
    1. **Analyze:** Look at the Context. Does it answer the user's request?
       - If YES: Explain it using the source material.
       - If NO: You **MUST** use the `scrape_website` or `Google Search` tool to find the answer.
    
    2. **The Feynman Technique:**
       - **Simple Language:** No jargon. Explain it like I'm 12 years old.
       - **Mandatory Analogy:** You MUST use a concrete, real-world analogy (e.g., "Think of a CPU like a chef in a kitchen...").
       - **Deep Understanding:** Don't just summarize; reveal the "why" and "how".
    
    3. **Citation:** If you used the context, mention "According to the document...". If you used a tool, mention the source.
    """
    
    # Use SystemMessage to properly set the AI's persona
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    print("💡 Feynman Agent: Generating explanation...")
    
    # --- 5. Invoke ---
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}