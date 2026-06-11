import os
from .tools.news_tools import get_news
from .tools.ai_retry import safe_generate_content

def run_news_analyst(state):
    ticker = state["ticker"]
    errors = state.get("error_flags", {})
    
    try:
        news_items = get_news(ticker)
        prompt = f"""
        Analyze the following real-time news data for asset ticker: {ticker}.
        Articles: {str(news_items)}
        
        Provide:
        1. An executive 1-2 sentence summary of each item.
        2. Assign a precision sentiment score scaling from -1.0 (extremely bearish) to +1.0 (extremely bullish).
        3. Determine an overall macro-news sentiment classification.
        """
        
        response_text = safe_generate_content(model="meta-llama/llama-3.3-70b-instruct:free", contents=prompt)
        return {
            "news_data": news_items,
            "news_report": response_text,
            "error_flags": {**errors, "news_failed": False}
        }
    except Exception as e:
        return {
            "news_data": [],
            "news_report": f"[News processing pipeline encountered an error: {str(e)}]",
            "error_flags": {**errors, "news_failed": True}
        }