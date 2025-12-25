from src.utils.llm_setup import get_llm

def quiz_node(state):
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # --- RAG Logic ---
    print("🔍 Retrieving relevant context for quiz...")
    retriever = get_retriever()
    
    # Search the vector DB for content relevant to the user's request
    relevant_docs = retriever.invoke(user_input)
    
    # Combine the found chunks into one context string
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    if not context_text:
        # Fallback if DB is empty or search fails
        context_text = state.get("file_content", "")[:5000]

    instruction = f"Create a comprehensive exam about '{user_input}' based on the context."

    prompt = f"""
    You are a Professor creating a quiz.
    
    Context (Derived from Course Materials):
    {context_text}
    
    Task:
    {instruction}
    
    Format:
    - Ask **five** multiple choice questions.
    - Provide 4 options (A, B, C, D).
    - **DO NOT** reveal the answer yet.

    """
    
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_step": "quiz_grade"
    }