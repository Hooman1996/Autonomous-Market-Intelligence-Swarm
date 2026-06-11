import os
from .tools.market_data import get_ohlcv
from .tools.ai_retry import safe_generate_content

def run_technical_analyst(state):
    ticker = state["ticker"]
    errors = state.get("error_flags", {})
    
    try:
        market_payload = get_ohlcv(ticker)
        if market_payload.get("status") == "error":
            raise RuntimeError(market_payload.get("message", "Data processing node failure"))
            
        prompt = f"""
        You are an Expert Technical Analyst Swarm Node. Analyze this historical pricing tracking matrix for {ticker}:
        Data Array: {str(market_payload.get('data', []))}
        
        Provide a professional breakdown containing:
        1. Current support and resistance lines based on short-term price discovery.
        2. Indicator evaluation: Interpret the values of SMA_50, SMA_200, RSI, and MACD.
        3. A crisp tactical execution stance (Bullish / Bearish / Neutral) with high-density justification.
        """
        
        response_text = safe_generate_content(model="google/gemma-4-31b-it:free", contents=prompt)
        return {
            "technical_report": response_text,
            "error_flags": {**errors, "technical_failed": False}
        }
    except Exception as e:
        return {
            "technical_report": f"[Technical Engine Fallback active. Raw Signal Trace: {str(e)}]",
            "error_flags": {**errors, "technical_failed": True}
        }