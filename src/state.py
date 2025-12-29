from typing import TypedDict, Annotated, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages : Annotated[List[BaseMessage], add_messages]
    file_content : Optional[str] # file PDF if loaded
    mode: Optional[str] # mode determined by classifer
    chunk_count: int
    quiz_answers: Optional[str]