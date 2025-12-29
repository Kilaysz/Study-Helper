from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever
from src.tools_advisor import ncku_faculty_search , get_advisor_tool

def advisor_node(state):
    """
    Academic Advisor Agent:
    Matches students to NCKU Professors based on research interests.
    Uses Vector Search (RAG) + Live Web Search (only for contact info).
    """
    llm = get_llm()
    user_project_idea = state["messages"][-1].content
    
    print(f"🎓 Advisor Agent: Searching for supervisors matching '{user_project_idea[:30]}...'")

    # 1. RAG Retrieval (Find matched professors from FACULTY DB)
    context_text = ""
    try:
        # Retrieve from FACULTY database
        retriever = get_retriever(k=200, db_type="faculty")
        relevant_docs = retriever.invoke(user_project_idea)
        
        # Filter for faculty_db documents
        prof_docs = [doc for doc in relevant_docs if doc.metadata.get("source") == "faculty_db"]
        if not prof_docs: prof_docs = relevant_docs 

        if prof_docs:
            context_text = "\n\n".join([doc.page_content for doc in prof_docs])
            print(f"   ✅ Found {len(prof_docs)} potential supervisors.")
    except Exception as e:
        print(f"   ⚠️ Retrieval failed: {e}")

    tools = get_advisor_tool()
    llm_with_tools = llm.bind_tools(tools)

    # 3. Construct Prompt (Clean Format + Strict JSON Rules)
    system_prompt = f"""
    You are an Expert Academic Advisor at NCKU CSIE.
    
    ### USER PROJECT IDEA
    "{user_project_idea}"
    
    ### CANDIDATE PROFESSORS (From Database)
    {context_text}
    
    ### TASK
    1. **Analyze Matches:** Identify the **single best matching professor** from the list above.
    2. **Verify (Optional):** If the database is missing the 'Email' or 'Lab Name', use `ncku_faculty_search` to find it. Do NOT search for reviews/social media.
    
    ### ⚠️ CRITICAL TOOL USE RULES ⚠️
    - **DO NOT** write "I will search for..." or "Let me check..."
    - **DO NOT** output any text before the tool call.
    - If you need to use a tool, output **ONLY** the tool call JSON.
    
    ### FINAL OUTPUT FORMAT
    (Do not use tables. Use the structure below strictly.)

    ## 🏆 Top Recommendation: [Professor Name]
    
    **🧪 Lab:** [Lab Name]  
    **📧 Email:** [Email Address]
    
    ### 🎯 Why this is a match?
    [Explain specific connection between user's idea and professor's research]

    ---
    ### 📝 Draft Email
    **Subject:** [Professional Subject Line]
    
    [Body of the email]
    """

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # 4. Invoke
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}