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
- 85–100: Small team (2–5 people), active in last 2 weeks, uses React/Flutter/Firebase/Node, clearly a product company
- 70–84: Small team, active in last month, partial stack overlap
- 50–69: Medium team or partial signals
- 0–49: Too big, wrong domain, no activity, services/consulting firm
- HARD REJECT: 11+ employees, services company (not product), no tech stack match, last activity > 60 days
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
  Examples: "React developer available — noticed you're building {product_type}"
             "Available to help ship {feature_area} this summer"
- Opening line: One sentence about what they're building. NOT "I came across your company". 
  Say something specific: "Your Flutter-based logistics tool caught my attention — the offline-first approach is hard to get right."
- Body (3 sentences max): 
  1. Two specific skills that match their stack
  2. One concrete proof point (a project or OSS contribution)
  3. Low-pressure offer: "Happy to do a small paid test task first" OR "Can share relevant code from similar projects"
- Closing: Single line. NOT "Looking forward to hearing from you." NOT "I hope this finds you well."
  Use: "If the timing works, let's talk." OR "Worth a quick call if you're open to it."
- Signature: Pranjal Jha | github.com/pranjal2004838 | pranjaljha703@gmail.com

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
