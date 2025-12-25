from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm_setup import get_llm

def message_classifier_node(state):
    """
    DETERMINES the intent (Mode).
    It does not route; it only updates the state with 'mode'.
    """

    # 2. HEURISTIC: File Upload with no text
    user_message = state["messages"][-1].content
    file_name = state.get("file_name", "") # Check for name
    
    if file_name and not user_message.strip():
        print("🧠 Classifier: File detected with no text -> Summarize.")
        return {"mode": "summarize"}

    # 3. LLM: Classify intent
    llm = get_llm()
    
    system_prompt = """
    You are the Intent Classifier for an AI Study Partner. 
    Classify the user's input into exactly one category:
    
    1. 'summarize' -> User wants an overview or explanation of the document.
    2. 'simplify'  -> User says "explain like I'm 5", "I don't understand", asks for an analogy, or wants a simple explanation.
    3. 'quiz'      -> User wants to take a test, asks for questions, or wants an exam (not for answering questions nor checking the quiz answers).
    4. 'query'     -> General chat, specific questions, web search, answering the quiz we give, or anything else.

    Context:
    - User has uploaded a file: {has_file}
    
    User Message: "{input}"
    
    Output ONLY the category name in lowercase. Do not add punctuation or explanation.
    """
    
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "has_file": "Yes" if file_name else "No",
            "input": user_message
        })
        
        decision = response.content.strip().lower()
        print(f"🧠 Classifier LLM Response: {decision}")
        # Cleanup response logic
        if "quiz" in decision: mode = "quiz"
        elif "simplify" in decision: mode = "simplify" # Matches "simplify" or "simplifier"
        elif "summarize" in decision: mode = "summarize"
        else: mode = "query"
        
        print(f"🧠 Classifier labeled intent as: {mode}")
        return {"mode": mode}
        
    except Exception as e:
        print(f"⚠️ Classifier failed: {e}. Defaulting to query.")
        return {"mode": "query"}