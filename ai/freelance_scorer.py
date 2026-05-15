from ai.gemini_client import call_gemini

FREELANCE_SCORE_PROMPT = """
You are evaluating a potential freelance lead for Pranjal Jha.

Pranjal's profile:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, REST APIs, MongoDB, MySQL, PHP, WordPress, Wix, Supabase, TypeScript
- Services: Custom booking/management apps, Wix websites + automation, Business dashboards, Canva websites for coaches, AI SaaS MVPs, Make/Zapier automations, Stripe/PayPal integrations.

Lead to evaluate:
Platform: {platform}
Title: {title}
Body: {body}
URL: {url}

Return ONLY a JSON object:
{{
  "score": <0-100>,
  "service_match": "<which of Pranjal's services fits this best, or null>",
  "fit_reason": "<AI Opinion: 1-2 sentences. Is this worth Pranjal's time? Why or why not?>",
  "urgency": "<high | medium | low>",
  "pain_point": "<one short sentence describing their main problem>",
  "disqualify_reason": "<null or: 'too low budget', 'wrong stack/platform', 'full-time job', 'just chatting/no intent'>",
  "pass": <true if score >= 50>
}}

Scoring rules:
- 85-100: Immediate need, explicitly asking to hire, matches Pranjal's exact services (e.g., "Need a Wix dev", "Looking for someone to build a booking app").
- 72-84: Needs help, might hire, partial match or slightly vague.
- 50-71: Discussing a problem but no clear intent to hire, or general tech question.
- 0-49: Tutorial, self-promotion, completely unrelated, or looking for a co-founder without pay.
"""

FREELANCE_MESSAGE_PROMPT = """
Write a DM/reply from Pranjal Jha to a potential freelance client.

The tone must be: professional but approachable, concise, focused on solving their specific problem. NOT salesy or desperate.

Pranjal's background:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, Wix, Automations

Target Lead:
- Platform: {platform}
- Title: {title}
- Pain point: {pain_point}
- Service match: {service_match}

Rules for the message:
- Opening: Acknowledge their specific problem/post. "Saw your post about {pain_point}."
- Body (2-3 sentences): Mention that you've solved similar issues or built similar things. Briefly mention relevant skills/experience. 
- Offer: Provide a small piece of free advice OR offer to jump on a quick no-pressure call to discuss.
- Closing: "Let me know if you'd like to chat." or similar.
- Do NOT include generic greetings like "Dear sir/madam" or "Hope this finds you well".
- Keep it under 100 words.

Return JSON:
{{
  "message": "<the full message body, plain text>"
}}
"""

def score_freelance_lead(lead_data: dict) -> dict:
    prompt = FREELANCE_SCORE_PROMPT.format(
        platform=lead_data.get('platform', 'Unknown'),
        title=lead_data.get('title', 'No Title'),
        body=lead_data.get('body', 'No Body'),
        url=lead_data.get('url', '')
    )
    return call_gemini(prompt)

def generate_freelance_message(lead_data: dict) -> dict:
    prompt = FREELANCE_MESSAGE_PROMPT.format(
        platform=lead_data.get('platform', 'Unknown'),
        title=lead_data.get('title', 'No Title'),
        pain_point=lead_data.get('pain_point', 'their issue'),
        service_match=lead_data.get('service_match', 'web development')
    )
    return call_gemini(prompt)
