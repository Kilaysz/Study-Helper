from src.utils.llm_setup import get_llm
from src.tools import get_all_tools

def feynman_node(state):
    """
    Explains complex topics simply using the Feynman Technique.
    Uses search tools to verify facts before explaining.
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    file_content = state.get("file_content", "")
    
    # 1. Bind Tools to the LLM
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # 2. Build Context
    context = ""
    if file_content:
        context = f"Reference Material (from uploaded file):\n{file_content[:15000]}...\n"
    
    # 3. Create a Robust Prompt
    prompt = f"""
    You are Richard Feynman, the famous physicist known for simple explanations.
    
    User Request: "{user_input}"
    
    {context}
    
    Task:
    1. If the user's question requires external facts not in the reference material, USE THE DEEP SEARCH TOOL immediately.
    2. Once you have the information, explain the core concept in simple, plain English (easy to understand).
    3. Use a real-world analogy (e.g., "Imagine a water pipe..." or "Think of it like a library...").
    4. Avoid jargon. If you must use a technical term, define it immediately in simple words.
    5. Cite your source if you used the search tool.
    """
    
    # Add the prompt to the message history so the model sees it
    messages_with_prompt = state["messages"] + [{"role": "user", "content": prompt}]
    
    print("💡 Feynman Agent: Thinking (and possibly searching)...")
    
    # 4. Invoke with Tools
    # The graph handles the actual tool execution loop via 'tools_condition'
    response = llm_with_tools.invoke(messages_with_prompt)
    
    return {"messages": [response]}