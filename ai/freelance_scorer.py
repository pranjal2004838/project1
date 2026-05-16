from ai.gemini_client import call_gemini

FREELANCE_SCORE_PROMPT = """
You are evaluating a potential freelance lead for Pranjal Jha.

Pranjal's profile:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, REST APIs, MongoDB, MySQL, PHP, WordPress, Wix, Supabase, TypeScript
- Services: Custom booking/management apps, Wix websites + automation, Business dashboards, Canva websites for coaches, AI SaaS MVPs, Zapier/Make/n8n automations, Stripe/PayPal integrations, workflow automation.

Lead to evaluate:
Platform: {platform}
Title: {title}
Body: {body}
URL: {url}

IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, just raw JSON.
Example of expected output format:
{{"score": 78, "hidden_pain": "manually copying spreadsheet data", "service_match": "Zapier automation + CRM sync", "fit_reason": "High urgency, skill match", "urgency": "high", "disqualify_reason": null, "pass": true}}

Now evaluate the lead above and return a JSON object with these exact keys:
- "score": an integer from 0 to 100 (NOT a string, NOT a placeholder — a real number like 72 or 88)
- "hidden_pain": infer the REAL problem behind their request
- "service_match": which of Pranjal's services solves this best (null if none)
- "fit_reason": 1-2 sentences — is this worth Pranjal's time and why
- "urgency": "high" | "medium" | "low"
- "disqualify_reason": null OR one of: "too low budget", "wrong stack/platform", "full-time job", "just chatting/no intent"
- "pass": true if score >= 50, false otherwise

Scoring rules — USE THE FULL 0-100 RANGE:
- 85-100: Clear hire intent + strong skill match + high urgency ("Need this today", "Budget ready")
- 70-84: Good match + tech overlap + active intent
- 50-69: Vague but interesting; suggests a problem you can solve
- 20-49: Discussion/low-intent but related to your skills
- 0-19: Completely unrelated or spam
"""

FREELANCE_MESSAGE_PROMPT = """
Write a DM/reply from Pranjal Jha to a potential freelance client.

The tone must be: professional but approachable, concise, focused on solving their specific problem. NOT salesy or desperate.

Pranjal's background:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, Wix, Zapier/Make/n8n automations, WordPress

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

IMPORTANT: Return ONLY valid JSON with this exact structure:
{{"message": "<the full message body, plain text>"}}
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
