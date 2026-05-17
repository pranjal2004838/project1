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

Return ONLY a JSON object matching this schema strictly:
{{
  "score": 85,
  "hidden_pain": "form to CRM sync",
  "service_match": "Wix websites + automation",
  "fit_reason": "They are looking for a developer to integrate Stripe and build automations, which matches your core skills.",
  "urgency": "high",
  "disqualify_reason": null,
  "pass": true
}}

Scoring rules:
- USE THE FULL 0-100 RANGE. Do not just use 0 or 100. Be granular (e.g., 72, 88).
- 85–100: Clear hire intent + tech match + high urgency (e.g., "Need this fixed today").
- 70–84: Potential match + tech overlap (e.g., "Looking for a React dev for next week").
- 50–69: Vague but interesting; suggests a problem you can solve.
- 20–49: Discussion or low-intent post, but related to your skills.
- 0–19: Completely unrelated or spam.
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
- Hidden Pain: {hidden_pain}
- Service Match: {service_match}

Rules for the message:
- Opening: Lead with what you noticed (the hidden pain). "Noticed you're struggling with {hidden_pain}."
- Body (2-3 sentences): Mention that you've solved similar issues using {service_match}. Briefly mention your 3 years of experience.
- Offer: Provide a small piece of free advice OR offer to jump on a quick no-pressure call to scope it out.
- Tone: Peer-to-peer. Confident. Not desperate.
- Do NOT include generic greetings like "Dear sir/madam" or "Hope this finds you well".
- Keep it under 100 words.

Return JSON object:
{{
  "message": "Write the full message body, plain text here"
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
        hidden_pain=lead_data.get('hidden_pain', 'their issue'),
        service_match=lead_data.get('service_match', 'web development')
    )
    return call_gemini(prompt)
