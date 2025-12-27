from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm_setup import get_llm

def message_classifier_node(state):
    """
    DETERMINES the intent (Mode).
    It does not route; it only updates the state with 'mode'.
    """
    user_message = state["messages"][-1].content
    
    # 1. Get the actual content (since you don't store file_name)
    file_content = state.get("file_content", "")
    
    # 2. HEURISTIC: File detected (has content) but no user text
    # If the user just uploaded a file and hit send, default to "summarize"
    if file_content and not user_message.strip():
        print("🧠 Classifier: File detected with no text -> Summarize.")
        return {"mode": "summarize"}

    # 3. LLM: Classify intent
    llm = get_llm()
    
    system_prompt = """
    You are the Intent Classifier.
    Classify the user's input into exactly one category:
    
    1. 'summarize' -> User wants an overview of the document.
    2. 'simplify'  -> User wants a simple explanation or analogy.
    3. 'quiz'      -> User wants a test/exam.
    4. 'advisor'   -> User asks for a professor, supervisor, lab, or mentor for a project.
    5. 'query'     -> General chat or specific questions.

    Context:
    - User has uploaded a file: {has_file}
    
    User Message: "{input}"
    
    Output ONLY the category name in lowercase.
    """
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            # Check if content exists to tell LLM "Yes"
            "has_file": "Yes" if file_content else "No",
            "input": user_message
        })
        
        decision = response.content.strip().lower()
        print(f"🧠 Classifier LLM Response: {decision}")
        
        if "quiz" in decision: mode = "quiz"
        elif "simplify" in decision: mode = "simplify"
        elif "summarize" in decision: mode = "summarize"
        elif "advisor" in decision: mode = "advisor"
        else: mode = "query"
        
        return {"mode": mode}
        
    except Exception as e:
        print(f"⚠️ Classifier failed: {e}. Defaulting to query.")
        return {"mode": "query"}