from typing import Literal

def route_decision(state) -> Literal["query", "summarize", "simplify", "quiz", "quiz_grade", "advisor"]:
    """
    Traffic Cop: Reads state['mode'] and directs to the correct node.
    """
    mode = state.get("mode", "query")

    # Map the mode string to the exact routing key defined in graph.py
    if mode == "simplify":
        return "simplify"
    elif mode == "summarize":
        return "summarize"
    elif mode == "quiz":
        return "quiz"
    elif mode == "quiz_grade":
        return "quiz_grade"
    elif mode == "advisor":
        return "advisor"
    else:
        # Default fallback
        return "query"