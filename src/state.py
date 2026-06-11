"""State definition and structured-output schemas for the graph."""
from typing import Annotated, TypedDict, Literal, List
from pydantic import BaseModel
from langgraph.graph.message import add_messages


class JobAppState(TypedDict):
    messages: Annotated[list, add_messages]
    jd: str
    cv: str
    research: str
    analysis: str
    cv_tailored: dict
    next: str


class SupervisorOutput(BaseModel):
    next: Literal["researcher", "analyzer", "writer", "FINISH"]
    
    
class CVSection(BaseModel):
    heading: str
    bullets: List[str]

class TailoredCV(BaseModel):
    name: str
    contact: str
    summary: str
    sections: List[CVSection]