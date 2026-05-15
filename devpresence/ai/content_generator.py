import os
import google.generativeai as genai
import random
from config import PROFILE, GEMINI_API_KEY

try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3.1-pro-preview') # Using the requested Gemini 3.1 Pro (Preview) model
    else:
        model = None
except:
    model = None

def generate_content(platform: str, context: str, content_type: str, tone: str) -> str:
    if not model:
        return "ERROR: Gemini model not initialized. Check your GEMINI_API_KEY."

    prompt = f"""
You are writing on behalf of Pranjal Jha, a developer marketing himself for freelance/internship work.

DEVELOPER PROFILE:
{PROFILE}

PLATFORM: {platform}
CONTENT TYPE: {content_type}
TONE: {tone}
CONTEXT (what we are responding to or the situation):
{context}

STRICT RULES:
1. Sound like a real human, NOT a bot or template
2. NEVER use phrases like "I hope this message finds you well", "I am reaching out", "synergy", "leverage"
3. NEVER be desperate or beg — be confident and matter-of-fact
4. Keep it SHORT — LinkedIn max 150 words, Reddit max 100 words, Discord max 60 words
5. Include GitHub link only when natural, not forced
6. Vary sentence structure — no two posts should sound alike
7. If replying to a hiring post, directly address what they need
8. If self-promo post, lead with VALUE or a result, not "I am a developer"
9. End with a soft CTA — "happy to chat", "DM me", "drop a comment"
10. NO hashtag spam — max 3 hashtags on LinkedIn, 0 on Reddit/Discord

Generate ONLY the post text. No explanation, no preamble.
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 500}
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {e}"
