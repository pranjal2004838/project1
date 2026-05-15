import random

TONES = {
    "casual": "Write like you're texting a friend. Short sentences. Real talk.",
    "professional": "Clean, confident, no fluff. Like a senior developer writing.",
    "story": "Open with a mini story or situation. Make it relatable.",
    "direct": "Lead with the result or offer. No warm-up. Get to the point.",
    "humble_brag": "Mention something impressive very casually, like it's no big deal.",
}

OPENERS_TO_AVOID = [
    "I am a developer",
    "I have X years of experience", 
    "I am looking for",
    "I hope",
    "I would like to",
    "As a developer",
    "Hi, my name is",
]

STRONG_OPENERS = [
    "Just merged a PR into Mozilla's codebase.",
    "30 clients later, here's what I've learned:",
    "Most Flutter apps fail because of one thing:",
    "Built a full-stack app for a US client this week.",
    "3 years of Fiverr taught me something nobody tells you:",
    "Honest question: when did REST APIs get so complicated?",
]

def get_unique_tone(platform: str, recent_posts: list) -> str:
    recent_tones = [p.get('tone') for p in recent_posts[-3:] if p.get('tone')]
    available = [t for t in TONES.keys() if t not in recent_tones]
    return random.choice(available) if available else random.choice(list(TONES.keys()))
