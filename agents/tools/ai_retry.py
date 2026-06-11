import os
import time
import random
import logging
from openai import OpenAI

logger = logging.getLogger("OpenRouterSwarm")

def safe_generate_content(model: str, contents: str, max_retries: int = 5, initial_delay: int = 4) -> str:
    """
    Executes a chat completion across OpenRouter verified free pools.
    Includes smart failover loops for 429s and guards against 400 Bad Requests.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL: OPENROUTER_API_KEY missing from environment variables.")
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        max_retries=0, 
        default_headers={
            "HTTP-Referer": "https://localhost:3000",
            "X-Title": "Autonomous Market Intelligence Swarm"
        }
    )
    
    # Introduce wider staggering gaps to avoid concurrent account-level burst limits
    stagger_time = random.uniform(2.0, 7.0)
    time.sleep(stagger_time)
    
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": contents}],
                timeout=45.0
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
            raise ValueError("Empty payload received from endpoint.")
            
        except Exception as e:
            err_msg = str(e)
            
            # CRITICAL FIX 1: If it's a 400 Bad Request, do not loop. Fail immediately to fallback.
            if "400" in err_msg or "bad_request" in err_msg.lower() or "not a valid model ID" in err_msg:
                logger.error(f"❌ Invalid Model ID detected ({model}). Bypassing retries and forcing immediate fallback routing.")
                break
            
            # Catch standard rate limiting codes
            if "429" in err_msg or "rate_limit" in err_msg.lower() or "exhausted" in err_msg.lower():
                sleep_duration = delay + random.uniform(2.0, 5.0)
                logger.warning(
                    f"⚠️ [OpenRouter Rate Limit] Model: {model} | "
                    f"Backing off for {sleep_duration:.2f}s (Attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(sleep_duration)
                delay *= 2 
            else:
                logger.warning(f"⚠️ Network exception encountered ({err_msg}). Retrying in {delay}s...")
                time.sleep(delay)
                
    # CRITICAL FIX 2: Diversified Fallback Pool
    # If a model goes down or is systematically rate-limited upstream, rotate options
    fallback_options = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "openai/gpt-oss-120b:free"
        "google/gemma-4-26b-a4b-it:free",

    ]
    
    # Filter out the model that just failed from our fallback list
    usable_fallbacks = [fb for fb in fallback_options if fb != model]
    
    for fallback_pool in usable_fallbacks:
        logger.error(f"⛔ Failover triggered. Attempting alternative routing lane: {fallback_pool}")
        try:
            time.sleep(3.0)  # Cool-down breather
            completion = client.chat.completions.create(
                model=fallback_pool,
                messages=[{"role": "user", "content": contents}],
                timeout=45.0
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
        except Exception as crash:
            logger.warning(f"⚠️ Backup lane {fallback_pool} also restricted. Trying next available asset...")
            continue

    raise RuntimeError("Swarm infrastructure completely gridlocked. All primary and fallback channels exhausted.")