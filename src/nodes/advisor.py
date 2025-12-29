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

    # --- 3. Retrieval (RAG) ---
    context_content = ""
    try:
        # Keep k=10 for safety
        retriever = get_retriever(k=50, db_type="faculty")
        relevant_docs = retriever.invoke(user_input)
        
        if relevant_docs:
            docs_text = []
            for doc in relevant_docs:
                name = doc.metadata.get("name", "Unknown")
                profile_link = doc.metadata.get("profile_url", "N/A")
                docs_text.append(f"NAME: {name}\nLINK: {profile_link}\nDATA: {doc.page_content}\n")
            
            context_content = "\n".join(docs_text)
            print(f"   ✅ Retrieved {len(relevant_docs)} candidates.")
        else:
            print("   ⚠️ No matching professors found.")
            
    except Exception as e:
        print(f"   ⚠️ Retrieval failed: {e}")

    # --- 4. System Prompt ---
    system_prompt = f"""
    You are an Expert Academic Advisor at NCKU CSIE.
    
    ### CANDIDATE DATA (From Internal Database)
    {context_content}
    
    ### STUDENT REQUEST
    "{user_input}"
    
    ### INSTRUCTIONS
    1. **Selection:** Pick the best matching professor from the list above.
    
    2. **Tool Usage Rules (STRICT):**
       - **DO NOT** use a tool named 'search'. It does not exist.
       - The ONLY valid tools are: `deep_research` and `ncku_faculty_search`.
       - If you don't need a tool, just answer directly.
    
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
        
        # Fallback: Force the LLM to just write text (no tools allowed)
        # We append a system message telling it to stop trying to search.
        fallback_msg = SystemMessage(content="Error: The search tool is unavailable. Please answer using ONLY the provided internal database context.")
        messages.append(fallback_msg)
        
        # Invoke the standard LLM (unbound)
        response = llm.invoke(messages)
        return {"messages": [response]}