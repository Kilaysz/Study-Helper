# src/nodes/query.py
from langchain_core.messages import SystemMessage
from src.utils.llm_setup import get_llm
from src.tools import get_all_tools

def query_node(state):
    """
    Handles general queries and injects formatting instructions.
    """
    llm = get_llm()
    
    # Bind tools
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # 2. Define the System Prompt for Formatting
    system_instruction = SystemMessage(content="""
    You are a helpful AI Study Partner
    please do some web search (required) to validate your answers.

    When answering user queries, always follow these    
    FORMATTING RULES:
    - Use **Markdown** for all responses.
    - Use **Bold** for key terms.
    - Use `### Headers` to organize long answers.
    - Use lists (bullets or numbers) for steps or facts.
    - If displaying data, use Markdown Tables.
    """)

    messages_with_prompt = [system_instruction] + state["messages"]
    
    print(f"🌐 Query Agent processing...")
    
    # 4. Invoke with the Prompt
    response = llm_with_tools.invoke(messages_with_prompt)
    
    return {"messages": [response]}