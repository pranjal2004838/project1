from ai.gemini_client import call_gemini

COLD_EMAIL_SCORE_PROMPT = """
You are evaluating a tech founder as a target for a cold email from Pranjal Jha.

Pranjal's profile:
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, Wix, Supabase
- Goal: Short-term contract, code review, or small paid test task.

Founder to evaluate:
Name: {founder_name}
Company: {company_name}
Stack: {tech_stack}
Company Size: {company_size}
Activity: {activity_signal}

Return ONLY a JSON object:
{{
  "score": <0-100>,
  "fit_reason": "<AI Opinion: Analyze if this founder/company is worth reaching out to. Even if the tech stack is slightly different, if it's an active Hyderabad startup, give it a fair score.>",
  "disqualify_reason": "<null or: 'massive company', 'not a tech product'>",
  "pass": <true if score >= 50>
}}
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
  3. Offer to take some technical debt or feature backlog off their hands to help them move faster.
- Closing: "Worth a quick chat?" or "If you need an extra set of hands, let me know."
- Do NOT include generic greetings like "Hope this finds you well".

Return JSON:
{{
  "subject": "<specific subject, not generic>",
  "message": "<plain text email body>"
}}
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
