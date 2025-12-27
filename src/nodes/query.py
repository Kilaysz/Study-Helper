# src/nodes/query.py

from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools
from src.utils.vector_store import get_retriever  

def query_node(state):
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    query = state["messages"][-1].content
    
    # --- 2. RAG Retrieval Logic (DEDICATED DB) ---
    print(f"🌐 Query Node: Retrieving context for: '{query}'...")
    
    context_content = ""
    try:
        retriever = get_retriever(k=10, db_type="user")
        relevant_docs = retriever.invoke(query)
        # Combine chunks
        if relevant_docs:
            context_content = "\n\n".join([doc for doc in relevant_docs if doc.metadata.get("source") == "user_upload"])
            print(f"   ✅ Found {len(relevant_docs)} relevant document chunks.")
        else:
            print("   ⚠️ No relevant document chunks found.")
            
    except Exception as e:
        print(f"   ⚠️ Retrieval skipped/failed: {e}")

    # Fallback: If retrieval found nothing (e.g., vague query like "hello"), 
    # use the raw file from state, but truncated safely.
    if not context_content:
        raw_file = state.get("file_content", "") or ""
        context_content = raw_file[:15000] # Safe fallback limit
        if raw_file:
            print("   ⚠️ Using raw file fallback.")

    answer_key = state.get("quiz_answers", "No active quiz.")

    # --- 3. Optimized System Prompt ---
    system_instruction = SystemMessage(content=f"""
    You are an expert AI Study Partner. 
    
    ### 1. CONTEXT DATA
    **QUERY:** {query}
    **Relevant Document Excerpts (User Uploads Only):** {context_content}
    
    **Quiz Answer Key (Hidden):** {answer_key}

    ### 2. YOUR GOAL
    Analyze the user's latest message and determine if they are:
    (A) **Submitting Answers** to the quiz.
    (B) **Asking a General Question**.

    ---
    ### 3. EXECUTION RULES

    #### IF (A) User is Submitting Answers (GRADING MODE):
    1. **STOP** and DO NOT search the web. Use the **Answer Key** as absolute truth.
    2. **Compare** the user's input to the Answer Key.
    3. **Generate Report:** Final Score and Corrections Table.

    #### IF (B) User is Asking Questions (TUTOR MODE):
    1. **Check Internal Context:** Does the 'Relevant Document Excerpts' section answer the question?
    2. **MANDATORY TOOL USAGE:** - If the document excerpts are missing the answer, you **MUST** use `deep_research` or `Google Search`.
       - **DO NOT** answer from your internal memory if the document doesn't cover it.
       - If input contains a link, use `scrape_website`.
    3. **Action:** Call the appropriate tool.
    4. **Citations:** Cite the uploaded document or the web source URL.
    """)

    messages_with_prompt = [system_instruction] + state["messages"]
    
    print("🌐 Query Node: Invoking LLM...")
    response = llm_with_tools.invoke(messages_with_prompt)

    return {"messages": [response]}