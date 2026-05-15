from ai.gemini_client import call_gemini

HYDERABAD_SCORE_PROMPT = """
You are evaluating a Hyderabad-based startup as a target for Pranjal Jha to reach out to.

Pranjal's profile:
- 3rd year ECE student at JNTUH Hyderabad, available full-time for 2 months (summer)
- 3 years freelancing, 30+ projects delivered
- Skills: React, Flutter, Firebase, Node.js, REST APIs, MongoDB, MySQL, PHP, WordPress, Wix, Supabase, TypeScript
- OSS: PRs merged into Mozilla, Zulip, OpenFoodFacts
- Location advantage: He is in Hyderabad — can meet in person if needed
- Seeking: Paid internship OR short-term contract (2 months), ₹8,000–20,000/month

Startup to evaluate:
Company: {company_name}
Source: {source}
Description: {description}
Tech stack detected: {tech_stack}
Company size: {company_size}
Last activity: {last_activity}
Website: {company_url}
GitHub: {github_url}

Return ONLY a JSON object:
{{
  "score": <0-100>,
  "fit_reason": "<AI Opinion: Be honest. Even if the stack isn't a perfect match, analyze if they could use Pranjal's skills.>",
  "stack_overlap": ["<matching skills>"],
  "urgency_signal": "<what suggests they might need help: recent launch, active commits, small team, etc.>",
  "disqualify_reason": "<null or: 'massive company', 'not a tech product'>",
  "pass": <true if score >= 50>,
  "suggested_contact_approach": "<direct email | github issue | website contact form>"
}}

Scoring rules:
- USE THE FULL 0-100 RANGE. Do not just use 0 or 100. Be granular (e.g., 72, 88).
- 85–100: Perfect match. Small team (2-5 people), active in last 2 weeks, uses your core stack (React/Flutter/Node), product-focused.
- 70–84: Strong match. Active team, partial stack match, or clear technical need.
- 50–69: Moderate match. Might be worth a quick message.
- 20–49: Weak match. Wrong stack or too big, but still a tech company.
- 0–19: Not a startup or completely dead activity.
"""

HYDERABAD_EMAIL_PROMPT = """
Write a cold outreach email from Pranjal Jha to a Hyderabad startup.

THIS IS NOT A JOB APPLICATION. This is a developer reaching out to collaborate.
The tone must be: confident, peer-to-peer, no desperation, no flattery.

Pranjal's background:
- 3 years freelancing, 30+ projects across React, Flutter, Firebase, Node
- OSS contributions merged into: Mozilla, Zulip, OpenFoodFacts
- Available full-time for 2 months this summer
- CURRENTLY IN HYDERABAD — can meet in person
- GitHub: github.com/pranjal2004838

Target startup:
- Company: {company_name}
- What they build: {description}
- Their tech stack: {tech_stack}
- Why it's a match: {fit_reason}
- Urgency signal: {urgency_signal}

Rules for the email:
- Subject line: SPECIFIC to what they're building. NOT "Internship Inquiry". NOT "Collaboration Request".
  Examples: "React developer available — noticed you're building {company_name}"
             "Available to help ship your {tech_stack} product this summer"
- Body: Use THIS EXACT angle and structure (adapt the placeholders to fit):
  "Hyderabad dev here (JNTUH ECE). Your product uses {tech_stack}. I've shipped 30+ projects, contributed to Mozilla and Zulip. Available full-time 2 months. Can meet in person. Worth a quick call?"
  (Do not copy it word-for-word if it sounds weird, but keep it extremely close to this length and punchiness.)
- Signature: 
  Pranjal Jha
  github.com/pranjal2004838
  pranjaljha703@gmail.com

NEVER SAY: "I am passionate", "I am hardworking", "I would be honored", "leverage", "synergy"
NEVER MENTION: JNTUH, CGPA, "student", "internship" in the subject line

Return JSON:
{{
  "subject": "<the email subject line>",
  "message": "<the full email body, plain text, no HTML>"
}}
"""

def score_hyderabad_startup(startup_data: dict) -> dict:
    prompt = HYDERABAD_SCORE_PROMPT.format(**startup_data)
    return call_gemini(prompt)

def generate_hyderabad_email(startup_data: dict) -> dict:
    prompt = HYDERABAD_EMAIL_PROMPT.format(**startup_data)
    return call_gemini(prompt)
