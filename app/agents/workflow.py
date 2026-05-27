from langgraph.graph import StateGraph, END

from app.agents.state import ResearchState

from app.agents.planner import planner_node
from app.agents.researcher import researcher_node
from app.agents.summarizer import summarizer_node

workflow = StateGraph(ResearchState)

workflow.add_node(
    "planner",
    planner_node
)

workflow.add_node(
    "researcher",
    researcher_node
)

workflow.add_node(
    "summarizer",
    summarizer_node
)

workflow.set_entry_point("planner")

workflow.add_edge(
    "planner",
    "researcher"
)

workflow.add_edge(
    "researcher",
    "summarizer"
)

workflow.add_edge(
    "summarizer",
    END
)

graph = workflow.compile()
