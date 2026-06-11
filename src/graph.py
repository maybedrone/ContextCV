"""Graph wiring: nodes, edges, checkpointer, and HITL interrupt. Exports `app`."""
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from src.config import tools
from src.state import JobAppState
from src.agents import Supervisor, Researcher, Analyzer, Writer, should_continue


def build_app():
    graph = StateGraph(JobAppState)

    # Nodes
    graph.add_node("supervisor", Supervisor)
    graph.add_node("researcher", Researcher)
    graph.add_node("researcher_tools", ToolNode(tools))
    graph.add_node("analyzer", Analyzer)
    graph.add_node("writer", Writer)

    # Edges
    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "researcher": "researcher",
            "analyzer": "analyzer",
            "writer": "writer",
            "FINISH": END,
        },
    )

    graph.add_conditional_edges(
        "researcher",
        should_continue,
        {"tools": "researcher_tools", "end": "supervisor"},
    )
    graph.add_edge("researcher_tools", "researcher")

    graph.add_edge("analyzer", "supervisor")
    graph.add_edge("writer", "supervisor")

    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["writer"])


app = build_app()