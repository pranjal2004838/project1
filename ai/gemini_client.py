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


def _safe_int(value, default=50) -> int:
    """
    Safely convert a value to int.
    Handles cases where Gemini returns the template placeholder like '<0-100>' literally.
    Falls back to `default` (50 = 'Maybe') if value is not a real integer.
    """
    if isinstance(value, int):
        return max(0, min(100, value))
    if isinstance(value, float):
        return max(0, min(100, int(value)))
    if isinstance(value, str):
        # Try to extract first number from the string
        match = re.search(r'\d+', value)
        if match:
            return max(0, min(100, int(match.group(0))))
    return default


def _sanitize_result(result: dict) -> dict:
    """
    Post-process Gemini's JSON output to ensure score is always a real int (0-100).
    If score is missing or is a template placeholder, assign a reasonable default.
    """
    if "score" in result:
        result["score"] = _safe_int(result["score"], default=50)
    else:
        result["score"] = 50  # Default to "Maybe" if Gemini forgot to include it

    # Ensure pass field is consistent with score
    if "pass" not in result:
        result["pass"] = result["score"] >= 50

    return result


def call_gemini(prompt: str, max_tokens: int = 2000) -> dict:
    """
    Call Gemini and parse JSON response.
    Uses 2000 tokens (enough for full emails).
    Retries once on failure.
    Always returns a dict with a valid integer 'score'.
    """
    if not model:
        return {
            "error": "GEMINI_API_KEY not found",
            "pass": False,
            "score": 0,
            "message": "Set GEMINI_API_KEY in Streamlit Cloud Secrets.",
            "subject": ""
        }

    for attempt in range(2):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": max_tokens,
                }
            )
            text = response.text.strip()

            # Strip markdown code fences (```json ... ```)
            text = re.sub(r'^```(?:json)?\n?', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\n?```$', '', text)
            text = text.strip()

            # Try direct JSON parse
            try:
                result = json.loads(text)
                return _sanitize_result(result)
            except json.JSONDecodeError:
                pass

            # Fallback: extract first {...} block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group(0))
                    return _sanitize_result(result)
                except json.JSONDecodeError:
                    pass

            print(f"[!] Gemini returned non-JSON (attempt {attempt+1}): {text[:150]}")

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
