from langgraph.graph import StateGraph, END
from src.state import GraphState
from src.nodes.fetch import fetch_emails
from src.nodes.analyze import analyze_emails
from src.nodes.digest import create_digest
from src.nodes.draft import create_draft

def create_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("fetch", fetch_emails)
    workflow.add_node("analyze", analyze_emails)
    workflow.add_node("digest", create_digest)
    workflow.add_node("draft", create_draft)

    # Define edges
    workflow.set_entry_point("fetch")
    
    workflow.add_edge("fetch", "analyze")
    workflow.add_edge("analyze", "digest")
    workflow.add_edge("digest", "draft")
    workflow.add_edge("draft", END)

    app = workflow.compile()
    return app
