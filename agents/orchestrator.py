import os
from typing import Dict, List, Any, TypedDict, Annotated  # Added Annotated here
from langgraph.graph import StateGraph, START, END
import logging

from .news_agent import run_news_analyst
from .technical_agent import run_technical_analyst
from .sentiment_agent import run_sentiment_analyst
from .risk_agent import run_risk_assessor
from .editor_agent import run_editor_agent

# New reducer function to handle parallel state dictionary writes safely
def merge_error_flags(left: dict, right: dict) -> dict:
    base = dict(left) if left else {}
    update = dict(right) if right else {}
    base.update(update)
    return base

class SwarmState(TypedDict):
    ticker: str
    news_data: List[Dict[str, Any]]
    news_report: str
    technical_data: Dict[str, Any]
    technical_report: str
    chart_path: str
    sentiment_data: List[Dict[str, Any]]
    sentiment_report: str
    risk_report: str
    final_brief: str
    # Wrapped with Annotated and our custom dictionary reducer
    error_flags: Annotated[dict, merge_error_flags]

logger = logging.getLogger("Orchestrator")

def create_swarm_graph():
    workflow = StateGraph(SwarmState)
    
    # Declare operational logic nodes
    workflow.add_node("NewsAnalyst", run_news_analyst)
    workflow.add_node("TechnicalAnalyst", run_technical_analyst)
    workflow.add_node("SentimentAnalyst", run_sentiment_analyst)
    workflow.add_node("RiskAssessor", run_risk_assessor)
    workflow.add_node("Editor", run_editor_agent)
    
    # Establish parallel entry vector execution patterns (Fan-out from START)
    workflow.add_edge(START, "NewsAnalyst")
    workflow.add_edge(START, "TechnicalAnalyst")
    workflow.add_edge(START, "SentimentAnalyst")
    
    # Fan-in configurations linking to risk evaluation
    workflow.add_edge("NewsAnalyst", "RiskAssessor")
    workflow.add_edge("TechnicalAnalyst", "RiskAssessor")
    workflow.add_edge("SentimentAnalyst", "RiskAssessor")
    
    # Downstream execution flow to synthesis terminal
    workflow.add_edge("RiskAssessor", "Editor")
    workflow.add_edge("Editor", END)
    
    return workflow.compile()