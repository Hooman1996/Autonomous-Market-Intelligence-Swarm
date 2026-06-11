import os
import json
from .tools.ai_retry import safe_generate_content

def run_editor_agent(state):
    ticker = state["ticker"]
    chart_p = state.get("chart_path", "[Service unavailable]")
    
    past_memory_context = ""
    memory_file = "memory/past_briefs.json"
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                history = json.load(f)
                filtered = [h for h in history if h.get("ticker") == ticker]
                if filtered:
                    past_memory_context = f"Contextual historical brief trends from prior assessment: {filtered[-1].get('summary')}"
        except Exception:
            past_memory_context = ""

    prompt = f"""
    You are the Chief Intelligence Editor. Synthesize the sub-agent output streams for asset: {ticker} into an executive decision brief.
    
    {past_memory_context}
    
    Sub-Agent Input Transcripts:
    - Technical Intelligence Report: {state.get('technical_report')}
    - Global News Stream Analysis: {state.get('news_report')}
    - Open Market Crowd Sentiment: {state.get('sentiment_report')}
    - Integrated Risk Framework: {state.get('risk_report')}
    
    Construct a Markdown Report adhering exactly to this organizational flow:
    # Autonomous Intelligence Brief: {ticker}
    ## Executive Summary
    ## Technical Outlook
    Render exactly this link structure for visualization: ![Chart]({chart_p})
    ## News & Sentiment Overview
    ## Risk Assessment
    ## Contradictions Matrix
    (Explicitly find, cross-reference, and evaluate structural disparities if technical indicators and crowds/news don't map to unified vectors. If synchronized, identify the latent vulnerability.)
    
    Footer: "Generated autonomously by AI Market Intelligence Swarm"
    """
    
    response_text = safe_generate_content(model="nousresearch/hermes-3-405b:free", contents=prompt)
    return {"final_brief": response_text}