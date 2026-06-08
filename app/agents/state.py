from typing import TypedDict, List, Dict, Any, Optional

class ResearchState(TypedDict):
    project_id: int
    session_id: str
    question: str
    messages: List[Dict[str, Any]]
    plan: str
    research: str
    answer: str
    mode: Optional[str]
