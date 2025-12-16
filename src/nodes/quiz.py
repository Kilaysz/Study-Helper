from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever

def quiz_node(state):
    """
    Generates a quiz based on the uploaded file (RAG) or the user's topic.
    Sets 'next_step' to ensure the user's next reply goes to the Grader.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # 1. Determine Context
    context_text = ""
    retriever = get_retriever()
    
    if retriever:
        print("🧠 Quiz Agent: Fetching diverse chunks from Vector DB...")
        # Use MMR to get diverse chunks for a better quiz
        try:
            docs = retriever.invoke(
                "key concepts definitions summary", 
                # search_kwargs={"k": 3, "fetch_k": 10} # Optional advanced tuning
            )
            for i, doc in enumerate(docs):
                context_text += f"\n--- EXCERPT {i+1} ---\n{doc.page_content}\n"
            
            instruction = "Create ONE multiple-choice question that requires synthesizing information from these excerpts."
        except Exception as e:
            print(f"⚠️ Vector DB Error: {e}")
            context_text = "Topic: General Knowledge"
            instruction = "Create a generic test question."
    else:
        # Fallback if no file uploaded
        context_text = f"Topic: {user_input}"
        instruction = f"Create a conceptual multiple-choice question about '{user_input}'."

    # 2. Generate Question
    prompt = f"""
    You are a Professor creating a quiz.
    
    Context:
    {context_text}
    
    Task:
    {instruction}
    
    Format:
    - Ask **only one** question.
    - Provide 4 options (A, B, C, D).
    - **DO NOT** reveal the answer yet.
    """
    
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_step": "quiz_grade"  # <--- CRITICAL: Forces next user input to go to Grader
    }