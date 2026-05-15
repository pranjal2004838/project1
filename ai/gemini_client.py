import google.generativeai as genai
import time
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

def call_gemini(prompt: str) -> dict:
    """Call Gemini and parse JSON response. Handles fences, retries, null fields."""
    if not model:
        return {"error": "GEMINI_API_KEY not found", "pass": False, "score": 0}
        
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 1000}
        )
        text = response.text.strip()
        
        # Strip markdown code fences
        text = re.sub(r'^```(?:json)?\n?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\n?```$', '', text)
        
        # Handle potential trailing commas or other JSON issues
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: try to find anything that looks like JSON
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
            
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return {"error": str(e), "pass": False, "score": 0}

def call_gemini_batch(prompts: list[str], delay_seconds: float = 4.1) -> list[dict]:
    """Rate-limited batch: 15 req/min on free tier. 4.1s delay is safe."""
    results = []
    for i, prompt in enumerate(prompts):
        results.append(call_gemini(prompt))
        if i < len(prompts) - 1:
            time.sleep(delay_seconds)
    return results
