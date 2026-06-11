import os
from .tools.ai_retry import safe_generate_content

def run_risk_assessor(state):
    ticker = state["ticker"]
    errors = state.get("error_flags", {})
    
    try:
        prompt = f"""
        You are the Risk Officer Core Swarm Node. Your job is to poke holes in the general consensus.
        Assess systemic exposure metrics for asset profile: {ticker}.
        
        Current contextual state data:
        - Technical Vector: {state.get('technical_report', 'Pending processing')}
        - News Vector: {state.get('news_report', 'Pending processing')}
        
        Deliver a calculated Risk Framework covering:
        1. Tail risk and liquidation clustering zones.
        2. Macro correlation vulnerabilities (interest rate impacts, geopolitical shifts, cross-asset shocks).
        3. Maximum drawdown thresholds and safety buffer recommendations.
        """
        
        response_text = safe_generate_content(model="qwen/qwen3-next-80b-a3b-instruct:free", contents=prompt)
        return {
            "risk_report": response_text,
            "error_flags": {**errors, "risk_failed": False}
        }
    except Exception as e:
        return {
            "risk_report": "[Risk evaluation engine resting on baseline conservative safety models.]",
            "error_flags": {**errors, "risk_failed": True}
        }