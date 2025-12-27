from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition 

from src.state import AgentState
from src.tools import get_all_tools

# Node Imports
from src.nodes.classifier import message_classifier_node
from src.nodes.router import route_decision
from src.nodes.query import query_node
from src.nodes.simplifier import feynman_node 
from src.nodes.summarizer import summarizer_node
from src.nodes.quiz import quiz_node
from src.nodes.advisor import advisor_node  

def build_graph():
    workflow = StateGraph(AgentState)

    # --- 1. Initialize Tool Node ---
    # This node will execute the tools (Tavily, Arxiv, etc.)
    tools = get_all_tools()
    tool_node_query = ToolNode(tools)
    tool_node_simplify = ToolNode(tools)
    tool_node_advisor = ToolNode(tools)

    # --- 2. Add All Nodes ---
    workflow.add_node("classifier", message_classifier_node) 
    workflow.add_node("query_agent", query_node)
    workflow.add_node("simplifier_agent", feynman_node) 
    workflow.add_node("summarizer_agent", summarizer_node)
    workflow.add_node("quiz_agent", quiz_node)
    workflow.add_node("advisor_agent", advisor_node)

    workflow.add_node("tools_query", tool_node_query)  
    workflow.add_node("tools_simplify", tool_node_simplify)
    workflow.add_node("tools_advisor", tool_node_advisor)

    # --- 3. Start at Classifier ---
    workflow.add_edge(START, "classifier")
    
    # --- 4. Router Logic ---
    workflow.add_conditional_edges(
        "classifier", 
        route_decision,
        {   
            "query": "query_agent", 
            "simplify": "simplifier_agent", 
            "summarize": "summarizer_agent", 
            "quiz": "quiz_agent",
            "advisor": "advisor_agent"
        }
    )

    # --- 5. Tool Execution Logic ---
    # Instead of ending immediately, check if the query_agent wants to call a tool
    workflow.add_conditional_edges(
        "query_agent",
        tools_condition,
        {
            "tools": "tools_query", # Map the default 'tools' output to our specific node
            END: END                # Map the default end signal to the Graph END
        }
    )
    # After the tool runs, go BACK to the query_agent to generate the answer
    workflow.add_edge("tools_query", "query_agent")

    workflow.add_conditional_edges(
        "simplifier_agent",
        tools_condition,
        {
            "tools": "tools_simplify", # Map the default 'tools' output to our specific node
            END: END                # Map the default end signal to the Graph END
        }
    )
    # After the tool runs, go BACK to the simplifier_agent to generate the answer
    workflow.add_edge("tools_simplify", "simplifier_agent")

    workflow.add_conditional_edges(
        "advisor_agent",
        tools_condition,
        {
            "tools": "tools_advisor", # Map the default 'tools' output to our specific node
            END: END                # Map the default end signal to the Graph END
        }
    )
    # After the tool runs, go BACK to the advisor_agent to generate the answer
    workflow.add_edge("tools_advisor", "advisor_agent")

    # --- 6. Standard Endings ---
    # (Note: query_agent can END via tools_condition if no tools are called)
    workflow.add_edge("simplifier_agent", END)
    workflow.add_edge("summarizer_agent", END)
    workflow.add_edge("quiz_agent", END)
    workflow.add_edge("advisor_agent", END)

    app = workflow.compile()
    return app