from ai.gemini_client import call_gemini

COLD_EMAIL_SCORE_PROMPT = """
You are evaluating a tech founder as a target for a cold email from Pranjal Jha.

Pranjal's profile:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, Wix, Supabase, WordPress, Zapier/Make/n8n automations
- Goal: Short-term contract, code review, or small paid test task.

Founder to evaluate:
Name: {founder_name}
Company: {company_name}
Stack: {tech_stack}
Company Size: {company_size}
Activity: {activity_signal}

IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, just raw JSON.
Example of expected output format:
{{"score": 68, "fit_reason": "Active founder with React stack, clear product focus", "disqualify_reason": null, "pass": true}}

Now evaluate the founder above and return a JSON object with these exact keys:
- "score": an integer from 0 to 100 (NOT a string, NOT a placeholder — a real number like 65 or 82)
- "fit_reason": 1-2 sentences — is this founder worth reaching out to and why
- "disqualify_reason": null OR one of: "massive company", "not a tech product"
- "pass": true if score >= 50

Scoring rules — USE THE FULL 0-100 RANGE, be granular:
- 85-100: Active small team founder, exact stack match, recently shipped
- 70-84: Strong match — active startup, partial stack overlap
- 50-69: Moderate — worth a try
- 20-49: Weak — different domain or large company
- 0-19: Not a startup or inactive
"""

COLD_EMAIL_GENERATE_PROMPT = """
Write a peer-to-peer cold email to a tech founder.

Target: {founder_name} at {company_name}
Context: {activity_signal}
Stack: {tech_stack}

Rules for the email:
- Subject line: Casual, peer-to-peer. e.g., "Loved what you shipped at {company_name}", "React dev — can help you ship faster"
- Tone: Peer-to-peer. "I can help you ship faster." DO NOT sound like a job applicant. DO NOT ask for an internship.
- Body (2-3 sentences):
  1. Acknowledge something specific they built or their tech stack.
  2. Briefly mention you are a dev with 3 years of experience and 30+ projects.
  3. Offer to take some technical debt or feature backlog off their hands.
- Closing: "Worth a quick chat?" or "If you need an extra set of hands, let me know."
- Do NOT include generic greetings like "Hope this finds you well".

IMPORTANT: Return ONLY valid JSON with this exact structure:
{{"subject": "<specific subject, not generic>", "message": "<plain text email body>"}}
"""

def score_cold_email_target(target_data: dict) -> dict:
    prompt = COLD_EMAIL_SCORE_PROMPT.format(
        founder_name=target_data.get('founder_name', 'Founder'),
        company_name=target_data.get('company_name', 'Company'),
        tech_stack=target_data.get('tech_stack', ''),
        company_size=target_data.get('company_size', ''),
        activity_signal=target_data.get('activity_signal', '')
    )
    return call_gemini(prompt)

def generate_founder_cold_email(target_data: dict) -> dict:
    prompt = COLD_EMAIL_GENERATE_PROMPT.format(
        founder_name=target_data.get('founder_name', 'Founder'),
        company_name=target_data.get('company_name', 'Company'),
        tech_stack=target_data.get('tech_stack', ''),
        activity_signal=target_data.get('activity_signal', '')
    )
    return call_gemini(prompt)
