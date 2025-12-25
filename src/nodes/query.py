from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools

def query_node(state):
    llm = get_llm()
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    query = state["messages"][-1].content
    
    file_content = state.get("file_content") or "No file uploaded."
    answer_key = state.get("quiz_answers", "No active quiz.")

    # Optimized System Prompt
    system_instruction = SystemMessage(content=f"""
    You are an expert AI Study Partner. 
    
    ### 1. CONTEXT DATA
   **QUERY:** {query}
   **Uploaded Document Content:** {file_content[:30000]} (truncated if too long)
    **Quiz Answer Key (Hidden):** {answer_key}

    ### 2. YOUR GOAL
    Analyze the user's latest message and determine if they are:
    (A) **Submitting Answers** to the quiz (e.g., "1. A, 2. B" or a list of answers).
    (B) **Asking a General Question** or chatting.

    ---
    ### 3. EXECUTION RULES

    #### IF (A) User is Submitting Answers (GRADING MODE):
    1. **STOP** and DO NOT search the web. Use the **Answer Key** and **Uploaded Document** as absolute truth.
    2. **Compare** the user's input to the Answer Key.
    3. **Enforce Completeness:** If the user provided fewer than 20 answers, mark the missing ones as "WRONG/UNANSWERED".
    4. **Generate Report:**
       - **Final Score:** (e.g., **14/20** - 70%)
       - **Corrections Table:** A Markdown table showing ALL questions: | Question # | User Answer | Correct Answer | Explanation |
       - **Summary:** Brief feedback on missed topics.

    #### IF (B) User is Asking Questions (TUTOR MODE):
    1. **Analyze the Request:** Does the user ask for information NOT in the uploaded document?
    2. **MANDATORY TOOL USAGE:** - If the uploaded document is empty or insufficient, you **MUST** use the `deep_research` (or `Google Search`) tool immediately.
       - **DO NOT** answer from your internal memory. You must verify facts with the tool.
       - if input contains link, scrape the website using `scrape_website` tool to get relevant information.
       - if deep research is hung, use Tavily Search tool as backup.
       - list 5 sources used in the answer.
    3. **Action:** Call the tool with a search query optimized for Google.
    4. **Citations:** After the tool returns data, write your answer and cite the source URL provided by the tool.
    5. **Formatting:** Use Markdown, bold key terms, and bullet points.
    """)

    messages_with_prompt = [system_instruction] + state["messages"]
    
    print("🌐 Query Node: Invoking LLM (Expecting Tool Call if needed)...")
    response = llm_with_tools.invoke(messages_with_prompt)

    print(response)
    
    return {"messages": [response]}