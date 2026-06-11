import os
import sys
import time
import requests
import yfinance as yf
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PriceMonitorNode")

def check_market_volatility(ticker: str, threshold: float = 2.0):
    """Tracks intra-hour movement profiles against established alert vectors."""
    logger.info(f"Triggering asynchronous interval observation loop for: {ticker}")
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    
    try:
        symbol_map = {"XAU/USD": "GC=F", "EUR/USD": "EURUSD=X"}
        yf_ticker = symbol_map.get(ticker.upper(), ticker)
        
        asset = yf.Ticker(yf_ticker)
        df = asset.history(period="2d")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        if len(df) < 2:
            logger.warning("Historical data boundaries inside short windows are insufficient.")
            return
            
        prior_close = df['Close'].iloc[-2]
        current_price = df['Close'].iloc[-1]
        
        pct_change = ((current_price - prior_close) / prior_close) * 100
        logger.info(f"Measured Delta status: {pct_change:.2f}% [Price: {current_price}]")
        
        if abs(pct_change) >= threshold:
            payload = {
                "text": f"🚨 *Swarm Pulse Alert* 🚨\nAsset `{ticker}` has realized high variance deviation: *{pct_change:.2f}%*\nCurrent Spot Execution: `{current_price:.4f}`\nContext Trigger: Macro validation protocol initiated."
            }
            if slack_url:
                requests.post(slack_url, json=payload, timeout=5)
                logger.info("Alert dispatched downstream to active endpoints.")
            else:
                logger.warning(f"Webhook connection properties missing. Alert generated inside local logs: {payload['text']}")
    except Exception as e:
        logger.error(f"Error checking market metrics: {str(e)}")

if __name__ == "__main__":
    # Designed for Cron execution configuration or interval infrastructure tasks
    target_ticker = sys.argv[1] if len(sys.argv) > 1 else "GC=F"
    check_market_volatility(target_ticker)