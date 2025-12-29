# src/nodes/query.py

import os
from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools
from src.utils.vector_store import get_retriever  

def query_node(state):
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    query = state["messages"][-1].content
    
    # --- 1. RAG Retrieval Logic (DEDICATED DB) ---
    print(f"🌐 Query Node: Retrieving context for: '{query}'...")
    
    context_content = ""
    try:
        retriever = get_retriever(k=30, db_type="user")
        relevant_docs = retriever.invoke(query)
        
        if relevant_docs:
            # FIX: Extracted .page_content (List[Document] -> List[str])
            docs_text = [doc.page_content for doc in relevant_docs]
            context_content = "\n\n".join(docs_text)
            print(f"   ✅ Found {len(relevant_docs)} relevant document chunks.")
        else:
            print("   ⚠️ No relevant document chunks found.")
            
    except Exception as e:
        print(f"   ⚠️ Retrieval skipped/failed: {e}")

    # Fallback: If retrieval found nothing, use raw file safe limit
    if not context_content:
        raw_file = state.get("file_content", "") or ""
        context_content = raw_file[:15000] 
        if raw_file:
            print("   ⚠️ Using raw file fallback.")

    # --- 2. Robust Answer Key Loading (State -> File -> Default) ---
    answer_key = state.get("quiz_answers")

    if not answer_key:
        # Fallback: Check if a key file exists from a previous turn
        key_path = os.path.join("uploads", "quiz_solutions.txt")
        if os.path.exists(key_path):
            try:
                with open(key_path, "r", encoding="utf-8") as f:
                    answer_key = f.read()
                print("   ✅ Loaded Quiz Answer Key from file backup.")
            except Exception as e:
                print(f"   ⚠️ Found answer key file but could not read: {e}")
    
    if not answer_key:
        answer_key = "No active quiz found. Treat this as a normal study question."

    # --- 3. Optimized System Prompt ---
    system_instruction = SystemMessage(content=f"""
    You are an expert AI Study Partner. 
    
    ### 1. CONTEXT DATA
    **QUERY:** {query}
    **Relevant Document Excerpts:** {context_content}
    
    **Quiz Answer Key (Hidden from User):** {answer_key}

    ### 2. YOUR GOAL
    Analyze the user's latest message and determine if they are:
    (A) **Submitting Answers** to the quiz.
    (B) **Asking a General Question**.

    ---
    ### 3. EXECUTION RULES

    #### IF (A) User is Submitting Answers (GRADING MODE):
    1. **STOP** and DO NOT search the web. Use the **Answer Key** above as absolute truth.
    2. **Compare** the user's input to the Answer Key.
    3. **Generate Report:** - Give a Final Score (e.g., 3/5).
       - Create a Corrections Table/List explaining ONLY the wrong answers.
       - Do not simply say "You are wrong". Explain WHY based on the key.
       - check the context_content to verify the answer

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