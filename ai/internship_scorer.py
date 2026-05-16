from ai.gemini_client import call_gemini

INTERNSHIP_SCORE_PROMPT = """
You are evaluating an internship or short-term contract opportunity for Pranjal Jha.

Pranjal's profile:
- 3rd year ECE student at JNTUH Hyderabad, available full-time for 2 months (summer)
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, REST APIs, MongoDB, MySQL, PHP, WordPress, Wix, Supabase, TypeScript, Zapier/Make/n8n automations
- OSS: PRs merged into Mozilla, Zulip, OpenFoodFacts
- Seeking: Paid internship OR short-term contract (2 months), Rs 8,000-20,000/month

Opportunity to evaluate:
Company: {company}
Role/Title: {name}
Source: {source}
Description: {description}
Stack: {stack}
Contact Info: {contact_type} - {contact_url}

IMPORTANT: Return ONLY a valid JSON object. No explanation, no markdown, just raw JSON.
Example of expected output format:
{{"score": 74, "stage": "MVP", "angle": "Your stack exactly, can start next week", "fit_reason": "They use React + Firebase, exact match", "stack_overlap": ["React", "Firebase"], "urgency_signal": "Recent GitHub activity", "disqualify_reason": null, "pass": true}}

Now evaluate the opportunity above and return a JSON object with these exact keys:
- "score": an integer from 0 to 100 (NOT a string, NOT a placeholder — a real number like 72 or 88)
- "stage": one of "Pre-MVP" | "MVP" | "Early traction" | "Growing"
- "angle": one of "I build MVPs in FlutterFlow/Bubble" | "Can handle your feature backlog" | "Firebase + Node scalability" | "Your stack exactly, can start next week" | "Automation + integration specialist"
- "fit_reason": 1-2 sentences — honest AI opinion, highlight any potential
- "stack_overlap": array of matching skills (can be empty [])
- "urgency_signal": what suggests they need someone now
- "disqualify_reason": null OR reason (only disqualify if absolutely non-tech or massive company)
- "pass": true if score >= 50

Scoring rules — USE THE FULL 0-100 RANGE, be granular (e.g., 72, 88):
- 85-100: Perfect match (exact stack + small team + active)
- 70-84: Strong match
- 50-69: Moderate match
- 20-49: Weak match (wrong stack or larger team)
- 0-19: Not a startup or completely inactive
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

Tone: Peer-to-peer. Confident. Not desperate. Mention you are in Hyderabad available for 2 months, but focus on your 3 years of freelancing and OSS contributions.

Rules for the message:
- The body MUST incorporate your specific outreach angle: "{angle}" seamlessly into the pitch.
- Keep it concise, 3-4 sentences max.

IMPORTANT: Return ONLY valid JSON with this exact structure:
{{"subject": "<Subject line>", "message": "<Plain text email body>"}}
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
