from src.utils.llm_setup import get_llm
from src.tools import get_all_tools # Ensure src/tools.py exists

def query_node(state):
    """
    Handles general queries using Tools (Web Search, Wikipedia, etc).
    """
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    # Bind tools so the LLM can use them if needed
    tools = get_all_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    print(f"🌐 Query Agent processing: '{user_input}'")
    
    # The LLM will decide: Answer directly OR Call a tool
    # LangGraph's prebuilt ToolNode (if used) would handle execution,
    # but here we rely on the model's internal reasoning or direct response.
    response = llm_with_tools.invoke(state["messages"])
    
    return {"messages": [response]}