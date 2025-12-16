from langgraph.graph import StateGraph, END, START
from src.state import AgentState

from src.nodes.classifier import message_classifier_node
from src.nodes.router import route_decision
from src.nodes.query import query_node
from src.nodes.simplifier import feynman_node 
from src.nodes.summarizer import summarizer_node
from src.nodes.quiz import quiz_node
from src.nodes.quiz_grader import quiz_grader_node

def build_graph():
    workflow = StateGraph(AgentState)

    # 1. Add All Nodes
    workflow.add_node("classifier", message_classifier_node) 
    workflow.add_node("query_agent", query_node)
    workflow.add_node("simplifier_agent", feynman_node) 
    workflow.add_node("summarizer_agent", summarizer_node)
    workflow.add_node("quiz_agent", quiz_node)
    workflow.add_node("quiz_grader", quiz_grader_node)

    workflow.add_edge(START, "classifier")
    
    # 3. Conditional Routing
    workflow.add_conditional_edges(
        "classifier", 
        route_decision,
        {   
            "query": "query_agent", 
            "simplify": "simplifier_agent", 
            "summarize": "summarizer_agent", 
            "quiz": "quiz_agent",
            "quiz_grade": "quiz_grader"
        }
    )

    # 4. Connect to END
    workflow.add_edge("query_agent", END) 
    workflow.add_edge("simplifier_agent", END) # Fixed name match
    workflow.add_edge("summarizer_agent", END)
    workflow.add_edge("quiz_agent", END)
    workflow.add_edge("quiz_grader", END)

    app = workflow.compile()

    return app