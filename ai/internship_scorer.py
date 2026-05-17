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

Return ONLY a JSON object matching this schema strictly:
{{
  "score": 85,
  "stage": "Growing",
  "angle": "Your stack exactly, can start next week",
  "fit_reason": "They are a growing startup looking for a developer to help with their frontend backlog, which is a great fit for your React experience.",
  "stack_overlap": ["React", "TypeScript"],
  "urgency_signal": "They recently posted about a feature launch backlog.",
  "disqualify_reason": null,
  "pass": true 
}}

Scoring rules:
- USE THE FULL 0-100 RANGE. Do not just use 0 or 100. Be granular (e.g., 72, 88).
- 85–100: Perfect match (stack + small team + active).
- 70–84: Strong match.
- 50–69: Moderate match.
- 20–49: Weak match (wrong stack or larger team).
- 0–19: Not a startup or completely inactive.
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

INTERNSHIP_EMAIL_PROMPT = """
Write a confident outreach message to a small tech company/startup asking for a short-term internship or contract.

Target: {company}
Role/Context: {name}
Stack: {stack}
Identified Stage: {stage}
Your Outreach Angle: {angle}
Why it's a fit: {fit_reason}

Tone: Peer-to-peer. Confident. Not desperate. Mention you are an ECE student in Hyderabad available for 2 months, but focus on your 3 years of freelancing and OSS contributions.

Rules for the message:
- The body MUST incorporate your specific outreach angle: "{angle}" seamlessly into the pitch.
- Keep it concise, 3-4 sentences max.

Return JSON object:
{{
  "subject": "React developer available — noticed company",
  "message": "Write the full plain text email body here"
}}
"""

def generate_internship_email(opp_data: dict) -> dict:
    prompt = INTERNSHIP_EMAIL_PROMPT.format(
        company=opp_data.get('company', 'Unknown'),
        name=opp_data.get('name', 'Unknown Role'),
        stack=opp_data.get('stack', ''),
        stage=opp_data.get('stage', 'Growing'),
        angle=opp_data.get('angle', 'Your stack exactly, can start next week'),
        fit_reason=opp_data.get('fit_reason', '')
    )
    return call_gemini(prompt)
