from ai.gemini_client import call_gemini

INTERNSHIP_SCORE_PROMPT = """
You are evaluating an internship or short-term contract opportunity for Pranjal Jha.

Pranjal's profile:
- 3rd year ECE student at JNTUH Hyderabad, available full-time for 2 months (summer)
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, REST APIs, MongoDB, MySQL, PHP, WordPress, Wix, Supabase, TypeScript
- OSS: PRs merged into Mozilla, Zulip, OpenFoodFacts
- Seeking: Paid internship OR short-term contract (2 months), ₹8,000–20,000/month

Opportunity to evaluate:
Company: {company}
Role/Title: {name}
Source: {source}
Description: {description}
Stack: {stack}
Contact Info: {contact_type} - {contact_url}

Return ONLY a JSON object:
{{
  "score": <0-100>,
  "fit_reason": "<one sentence: why Pranjal is a good fit for this role>",
  "stack_overlap": ["<matching skills>"],
  "urgency_signal": "<what suggests they need someone now>",
  "disqualify_reason": "<null or: 'senior only', 'unpaid', 'wrong stack', '11+ employees', 'not tech company'>",
  "pass": <true if score >= 78 AND disqualify_reason is null>
}}

Scoring rules:
- 85-100: Early stage startup (1-10 people), directly asking for a developer/intern in React/Flutter/Node, clear paid opportunity.
- 78-84: Good stack match, small company, but maybe slightly vague on terms.
- 50-77: Medium company, partial stack match, or competitive regular application portal.
- 0-49: Senior role required, unpaid, large corporate, or unrelated field.
"""

def score_internship_opportunity(opp_data: dict) -> dict:
    prompt = INTERNSHIP_SCORE_PROMPT.format(
        company=opp_data.get('company', 'Unknown'),
        name=opp_data.get('name', 'Unknown Role'),
        source=opp_data.get('source', 'Unknown Source'),
        description=opp_data.get('description', ''),
        stack=opp_data.get('stack', ''),
        contact_type=opp_data.get('contact_type', ''),
        contact_url=opp_data.get('contact_url', '')
    )
    return call_gemini(prompt)
