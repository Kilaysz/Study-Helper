from src.utils.llm_setup import get_llm

def feynman_node(state):
    """
    Explains complex topics simply using the Feynman Technique.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    file_content = state.get("file_content", "")
    
    # Use document context if available, otherwise just use the user's question
    context = ""
    if file_content:
        context = f"Reference Material:\n{file_content[:2000]}...\n"
    
    prompt = f"""
    You are Richard Feynman, the famous physicist known for simple explanations.
    
    User Request: "{user_input}"
    
    {context}
    
    Task:
    Explain the core concept in simple, plain English.
    1. Use a real-world analogy (e.g., "Imagine a water pipe..." or "Think of it like a library...").
    2. Avoid jargon. If you must use a technical term, define it immediately in simple words.
    3. Keep it concise but insightful.
    """
    
    print("💡 Generating Simple Explanation...")
    response = llm.invoke(prompt)
    
    return {"messages": [response]}