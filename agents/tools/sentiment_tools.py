import requests
import yfinance as yf
import logging

logger = logging.getLogger("SentimentTools")

def get_crowd_sentiment(ticker: str) -> list:
    """Fetches retail sentiment using keyless public endpoints, eliminating API key requirements."""
    # Format ticker for StockTwits (e.g., XAU/USD -> XAUUSD)
    st_ticker = ticker.replace("/", "").replace("=", "_").upper()
    
    # Attempt 1: StockTwits Public API (No auth required for basic streams)
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{st_ticker}.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=8)
        
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            if messages:
                logger.info(f"Successfully extracted StockTwits crowd sentiment for {st_ticker}")
                return [{"source": "StockTwits", "text": m.get("body", "")[:250]} for m in messages[:10]]
    except Exception as e:
        logger.warning(f"StockTwits extraction bypassed: {str(e)}")

    # Attempt 2: Yahoo Finance Secondary Stream (Robust proxy for retail/market chatter)
    try:
        logger.info("Pivoting to Yahoo Finance sentiment proxy.")
        yf_ticker = {"XAU/USD": "GC=F", "EUR/USD": "EURUSD=X"}.get(ticker.upper(), ticker)
        asset = yf.Ticker(yf_ticker)
        news = asset.news
        if news:
            return [{"source": "Yahoo Finance (Proxy)", "text": n.get("title", "") + " - " + n.get("publisher", "")} for n in news[:8]]
    except Exception as e:
        logger.warning(f"YF fallback failed: {str(e)}")

    # Attempt 3: Failsafe Synthetic Injection
    return get_mock_sentiment(ticker)

def get_mock_sentiment(ticker: str) -> list:
    logger.info("Using synthetic sentiment data to maintain swarm execution flow.")
    return [
        {"source": "Swarm_Simulated", "text": f"Massive volume coming into {ticker}, retail is heavily leaning bullish right now."},
        {"source": "Swarm_Simulated", "text": f"Warning signs on {ticker}, a lot of chatter about dumping positions before the macro data drops."}
    ]