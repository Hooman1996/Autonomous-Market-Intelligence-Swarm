import os
from .tools.ai_retry import safe_generate_content

def run_sentiment_analyst(state):
    ticker = state["ticker"]
    errors = state.get("error_flags", {})
    
    try:
        crowd_data = state.get("sentiment_data", "[Alternative volume signal streams active]")
        
        prompt = f"""
        You are the Crowd Sentiment Quant Node. Evaluate the real-time social streams and retail momentum indicators for {ticker}.
        Context Signal Trace: {str(crowd_data)}
        
        Synthesize:
        1. Retail crowd behavior vectors (Is FOMO building or are hands turning paper-thin?).
        2. Institutional block volume changes versus social chatter volume discrepancies.
        3. A definitive sentiment bias assessment.
        """
        
        response_text = safe_generate_content(model="nvidia/nemotron-3-super-120b-a12b:free", contents=prompt)
        return {
            "sentiment_report": response_text,
            "error_flags": {**errors, "sentiment_failed": False}
        }
    except Exception as e:
        return {
            "sentiment_report": "[Crowd pipeline throttled. Standardizing baseline neutral trend vectors.]",
            "error_flags": {**errors, "sentiment_failed": True}
        }