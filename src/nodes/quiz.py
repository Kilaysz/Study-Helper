from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.utils.vector_store import get_retriever

def quiz_node(state):
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # --- 1. RAG Retrieval ---
    print("🔍 Retrieving relevant context for quiz...")
    try:
        retriever = get_retriever(k=15, db_type="user") 
        relevant_docs = retriever.invoke(user_input)
        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
    except Exception as e:
        print(f"⚠️ Retrieval failed: {e}")
        context_text = ""
    
    # Fallback to raw file if retrieval returns nothing
    if not context_text:
        print("⚠️ Context empty, using raw fallback.")
        context_text = state.get("file_content", "")[:5000]

    prompt = f"""
    You are a Professor creating a quiz.
    
    ### CONTEXT
    {context_text}
    
    ### TASK
    Create a 5-question multiple choice exam about: "{user_input}".
    
    ### FORMAT
    1. **The Quiz:**
       - 5 Questions.
       - 4 Options (A, B, C, D) per question.
       - **DO NOT** mark the correct answer in this section.
    
    2. **The Divider:**
       - Print exactly this line: "### ANSWER KEY ###"
       
    3. **The Solutions:**
       - List the correct answer for each question (e.g., "1. A, 2. C...").
       - Provide a brief 1-sentence explanation for each.
    """
    
    # Use SystemMessage for better instruction adherence
    messages = [SystemMessage(content=prompt)]
    
    print("📝 Generating Quiz & Answer Key...")
    response = llm.invoke(messages)
    full_content = response.content
    
    # --- 3. Parse Output (Split Questions vs. Answers) ---
    if "### ANSWER KEY ###" in full_content:
        parts = full_content.split("### ANSWER KEY ###")
        quiz_for_user = parts[0].strip()
        answer_key = parts[1].strip()
    else:
        # Fallback if model forgets the separator
        quiz_for_user = full_content
        answer_key = "Error: Answer Key not generated."

    return {
        "messages": [{"role": "assistant", "content": quiz_for_user}],
        "quiz_answers": answer_key,
        "next_step": "quiz_grade" 
    }