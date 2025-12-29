from langchain_core.messages import SystemMessage, HumanMessage
from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever
from src.tools_advisor import get_advisor_tool

def advisor_node(state):
    llm = get_llm()
    
    # --- 1. Input Cleaning ---
    user_input = "General Advice"
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage) or getattr(msg, "type", "") == "human":
            user_input = msg.content
            break

    print(f"🎓 Advisor Agent: Analyzing '{user_input[:40]}...'")

    # --- 2. Bind Tools ---
    tools = get_advisor_tool()
    llm_with_tools = llm.bind_tools(tools)

    # --- 3. "Search All" Retrieval Strategy ---
    context_content = ""
    try:
        # STEP A: Retrieve EVERYONE (or a very high number)
        # This ensures we scan the entire JSON list mathematically.
        # 150 is safe for 'searching', but not for 'reading'.
        retriever = get_retriever(k=150, db_type="faculty") 
        all_matches = retriever.invoke(user_input)
        
        MAX_CHARS = 100000 
        current_chars = 0
        docs_text = []
        
        print(f"   📊 Scanning {len(all_matches)} total candidates...")
        
        for doc in all_matches:
            name = doc.metadata.get("name", "Unknown")
            profile_link = doc.metadata.get("profile_url", "N/A")
            
            # Format this professor's entry
            entry = f"NAME: {name}\nLINK: {profile_link}\nDATA: {doc.page_content}\n\n"
            
            # Check if adding this entry exceeds our safety limit
            if current_chars + len(entry) > MAX_CHARS:
                break # Stop adding, we are full!
                
            docs_text.append(entry)
            current_chars += len(entry)
            
        context_content = "".join(docs_text)
        print(f"   ✅ Selected top {len(docs_text)} matches (Context filled: {current_chars}/{MAX_CHARS} chars).")
            
    except Exception as e:
        print(f"   ⚠️ Retrieval failed: {e}")

    # --- 4. System Prompt ---
    system_prompt = f"""
    You are an Expert Academic Advisor at NCKU CSIE.
    
    ### CANDIDATE DATA (Ranked by Relevance)
    {context_content}
    
    ### STUDENT REQUEST
    "{user_input}"
    
    ### INSTRUCTIONS
    1. **Selection:** The list above contains the most relevant professors from the entire department. Pick the **single best match** (ONLY FROM THE LIST).
    
    2. **Tool Usage Rules (STRICT):**
       - **DO NOT** use a tool named 'search'. It does not exist.
       - The ONLY valid tools are: `deep_research` and `ncku_faculty_search`.
       - **Usage:** Only use `ncku_faculty_search` if the 'DATA' field is missing the Lab Name or Email.
    
    3. **Output Format:**
    ## 🏆 Top Recommendation: [Professor Name]
    **🧪 Lab:** [Extract from DATA]
    **🔗 Profile:** [Insert the LINK from DATA]
    **📧 Email:** [Extract from DATA]
    
    ### 🎯 Research Match
    [Explain match]
    
    ---
    ### 📝 Draft Email
    **Subject:** Prospective Student Inquiry - [Topic]
    [Body]
    """

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # --- 5. Execution (With Crash Protection) ---
    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
        
    except Exception as e:
        print(f"❌ Tool Call Error detected: {e}")
        print("   🔄 Retrying without tools to prevent crash...")
        
        fallback_msg = SystemMessage(content="Error: Tools unavailable. Answer using ONLY the provided database context.")
        messages.append(fallback_msg)
        response = llm.invoke(messages)
        return {"messages": [response]}