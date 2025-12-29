import os
from langchain_core.messages import SystemMessage, AIMessage
from src.utils.llm_setup import get_llm

def quiz_node(state):
    llm = get_llm()
    
    # 1. Get raw content (Limit to 50k chars to fit context)
    context_text = state.get("file_content", "")
    
    prompt = f"""
    You are a Professor creating a quiz based on the provided text.
    
    ### CONTEXT
    {context_text}
    
    ### TASK
    Create a 5-question multiple choice exam.
    
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
    
    # --- 2. Parse Output (Split Questions vs. Answers) ---
    if "### ANSWER KEY ###" in full_content:
        parts = full_content.split("### ANSWER KEY ###")
        quiz_for_user = parts[0].strip()
        answer_key = parts[1].strip()
    else:
        # Fallback if model forgets the separator
        quiz_for_user = full_content
        answer_key = "Error: Answer Key not generated. Please check the document content."

    # --- 3. Write Answer Key to File ---
    # We save it in 'uploads' so it gets cleaned up automatically by your delete endpoint
    output_dir = "uploads"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "quiz_solutions.txt")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(answer_key)
        print(f"✅ Answer Key saved to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to save answer key: {e}")

    # --- 4. Return ---
    # We still return 'quiz_answers' in state in case other nodes need it immediately
    return {
        "messages": [AIMessage(content=quiz_for_user)],
        "quiz_answers": answer_key,
        "next_step": "quiz_grade" 
    }