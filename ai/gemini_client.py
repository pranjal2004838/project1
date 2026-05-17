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
    print("[!] GEMINI_API_KEY not found — AI scoring and email generation will not work.")


def call_gemini(prompt: str, max_tokens: int = 2000) -> dict:
    """
    Call Gemini and parse JSON response.
    Uses 2000 tokens (enough for full emails).
    Retries once on failure.
    """
    if not model:
        return {"error": "GEMINI_API_KEY not found", "pass": False, "score": 0, "message": "Set GEMINI_API_KEY in Streamlit Cloud Secrets.", "subject": ""}

    for attempt in range(2):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json"
                }
            )
            text = response.text.strip()

            # Strip markdown code fences
            text = re.sub(r'^```(?:json)?\n?', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

            # Try parsing JSON
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Fallback: find first JSON object
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                # Last resort: if the response contains useful text, wrap it
                if len(text) > 20:
                    print(f"[!] Gemini returned non-JSON text: {text[:100]}")
                raise

        except Exception as e:
            print(f"[!] Gemini Error (attempt {attempt+1}): {e}")
            if attempt == 0:
                time.sleep(3)  # Wait before retry

    return {
        "error": "Gemini failed after retries",
        "pass": False,
        "score": 0,
        "message": "Email generation failed. Please try again.",
        "subject": "Follow-up"
    }


def call_gemini_batch(prompts: list, delay_seconds: float = 4.1) -> list:
    """Rate-limited batch: 15 req/min on free tier. 4.1s delay is safe."""
    results = []
    for i, prompt in enumerate(prompts):
        results.append(call_gemini(prompt))
        if i < len(prompts) - 1:
            time.sleep(delay_seconds)
    return results
