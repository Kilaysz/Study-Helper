from src.utils.llm_setup import get_llm
# REMOVED: from src.utils.vector_store import get_retriever

def quiz_node(state):
    """
    Generates a quiz based on the uploaded file content or the user's topic.
    NOTE: This version uses raw file_content (Context Stuffing), not Vector DB.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    file_content = state.get("file_content", "") # <-- Get the raw file content

    # --- RAG/Context Logic ---
    context_text = ""
    
    if file_content:
        # Use the first 4000 tokens of the document as context for the quiz
        # This is a simple form of RAG suitable for small files.
        context_text = file_content[:8000] 
        instruction = "Create a comprehensive exam based *only* on the provided document excerpt."
    else:
        # Fallback if no file uploaded
        context_text = f"Topic: {user_input}"
        instruction = f"Create a conceptual exam about '{user_input}'."

    # 2. Generate Question
    prompt = f"""
    You are a Professor creating a quiz.
    
    Context:
    {context_text}
    
    Task:
    {instruction}
    
    Format:
    - Ask **twenty** multiple choice questions and 5 essay questions.
    - Provide 4 options (A, B, C, D) for multiple choice questions.
    - **DO NOT** reveal the answer yet.
    """
    
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_step": "quiz_grade"
    }