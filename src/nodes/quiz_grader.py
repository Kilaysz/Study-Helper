from src.utils.llm_setup import get_llm 

def quiz_grader_node(state):
    """
    Evaluates the user's answer to the previous quiz question.
    Resets 'next_step' so the user can leave the quiz loop.
    """
    llm = get_llm()
    
    # Retrieve History
    history = state["messages"]
    user_answer = history[-1].content
    
    # Find the last question asked by the AI (usually the 2nd to last message)
    last_question = "Unknown Question"
    for msg in reversed(history[:-1]):
        if msg.role == "assistant":
            last_question = msg.content
            break

    prompt = f"""
    You are a Teacher grading a quiz.
    
    The Question you asked:
    "{last_question}"
    
    The Student's Answer:
    "{user_answer}"
    
    Task:
    1. Determine if the student is Correct or Incorrect.
    2. Provide a brief explanation of the correct answer.
    3. Ask if they want another question or want to stop.
    
    Start your response with either "✅ Correct!" or "❌ Incorrect.".
    """
    
    print(f"📝 Grading Answer: {user_answer}")
    response = llm.invoke(prompt)
    
    return {
        "messages": [response],
        "next_step": None  # <--- RESET: User is free to switch modes now
    }