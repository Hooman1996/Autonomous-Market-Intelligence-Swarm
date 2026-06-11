import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import logging

logger = logging.getLogger("ChartingTool")

def plot_chart(data_dict: dict, ticker: str) -> str:
    """Generates an evaluation chart tracking closing matrix and integrated Moving Averages."""
    try:
        os.makedirs("output", exist_ok=True)
        raw_df = data_dict.get("raw_df")
        
        if raw_df is None or not isinstance(raw_df, pd.DataFrame) or raw_df.empty:
            logger.warning("Insufficient dataframe matrix provided for visual charting. Building alternative trace.")
            return "[Service unavailable]"
            
        clean_ticker = ticker.replace("/", "_").replace("=", "")
        output_path = f"output/chart_{clean_ticker}.png"
        
        plt.figure(figsize=(10, 5))
        plt.plot(raw_df.index, raw_df['Close'], label='Close Price', linewidth=1.5)
        
        if 'SMA_50' in raw_df.columns:
            plt.plot(raw_df.index, raw_df['SMA_50'], label='50 SMA', linestyle='--', alpha=0.8)
        if 'SMA_200' in raw_df.columns:
            plt.plot(raw_df.index, raw_df['SMA_200'], label='200 SMA', linestyle='-.', alpha=0.8)
            
        plt.title(f"Market Intelligence System Metrics — Tracking Axis: {ticker}")
        plt.xlabel("Timeline Index")
        plt.ylabel("Value Standard Denomination")
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path
    except Exception as e:
        logger.error(f"Failed execution of chart production pipeline: {str(e)}")
        return "[Service unavailable]"