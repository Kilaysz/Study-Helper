from src.utils.llm_setup import get_llm 

def quiz_grader_node(state):
    """
    Evaluates the user's answer(s) to the exam.
    Resets 'next_step' so the user can leave the quiz loop.
    """
    llm = get_llm()
    
    # Retrieve History
    history = state["messages"]
    user_answer = history[-1].content
    
    # Find the last quiz content (the long exam)
    last_quiz_content = "Unknown Quiz"
    for msg in reversed(history[:-1]):
        if msg.role == "assistant":
            last_quiz_content = msg.content
            break

    prompt = f"""
    You are a Teacher grading an exam.
    
    The Exam you provided earlier:
    ---
    {last_quiz_content[:4000]}... (truncated for context window if needed)
    ---
    
    The Student's Input:
    "{user_answer}"
    
    Task:
    1. If the student provided answers (e.g. "1. A, 2. B"), grade them based on the exam context.
    2. If the student asked for the answer key, provide it.
    3. If the student answered a specific essay question, grade that specific answer.
    4. Be encouraging but strict on facts.
    5. give zero marks if the answer is wrong or blank.
    6. The response from user is the only source of truth for grading.
    
    Output the grading results or the answer key as requested.
    """
    
    print(f"📝 Grading Answer...")
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_step": None  # <--- RESET: User is free to switch modes now
    }