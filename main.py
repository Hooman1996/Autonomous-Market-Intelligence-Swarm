import os
import sys
import json
import argparse
from datetime import datetime
import logging


import os
from dotenv import load_dotenv

# 1. Force Python to read the .env file immediately
load_dotenv()

from agents.orchestrator import create_swarm_graph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SwarmRuntime")

def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Market Intelligence Swarm Node Execution")
    parser.add_argument("--ticker", type=str, default="GC=F", help="Target evaluation ticker mapping asset profiles")
    return parser.parse_args()

def write_to_memory(ticker: str, brief: str):
    memory_file = "memory/past_briefs.json"
    os.makedirs("memory", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ticker": ticker,
        "summary": brief[:300] + "..."
    }
    
    history = []
    if os.path.exists(memory_file):
        try:
            with open(memory_file, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []
            
    history.append(entry)
    with open(memory_file, 'w') as f:
        json.dump(history, f, indent=2)

def main():
    args = parse_arguments()
    ticker = args.ticker
    
    logger.info(f"Waking Multi-Agent Architecture Engine for profile: {ticker}")
    graph = create_swarm_graph()
    
    initial_state = {
        "ticker": ticker,
        "news_data": [],
        "news_report": "",
        "technical_data": {},
        "technical_report": "",
        "chart_path": "",
        "sentiment_data": [],
        "sentiment_report": "",
        "risk_report": "",
        "final_brief": "",
        "error_flags": {}
    }
    
    try:
        final_output = graph.invoke(initial_state)
        brief_markdown = final_output.get("final_brief", "# Operational Processing Error")
        
        # Save output document
        os.makedirs("output", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        clean_ticker = ticker.replace("/", "_").replace("=", "")
        filename = f"output/brief_{clean_ticker}_{date_str}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(brief_markdown)
            
        write_to_memory(ticker, brief_markdown)
        
        print("\n=== SYSTEM OUTPUT TERMINAL PREVIEW ===")
        print(brief_markdown)
        print("======================================\n")
        logger.info(f"Brief artifact deployment successful: {filename}")
        
    except Exception as e:
        logger.critical(f"Fatal crash inside pipeline thread orchestration: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()