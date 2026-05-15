import streamlit as st
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

st.set_page_config(
    page_title="Pranjal's Outreach Engine",
    layout="wide",
    page_icon="🎯"
)

# Session state init — stores all scan results IN MEMORY (persists across reruns in same session)
defaults = {
    'scan_running': False,
    'freelance_leads': [],
    'internship_opps': [],
    'cold_email_targets': [],
    'hyderabad_startups': [],
    'last_scan_freelance': None,
    'last_scan_internship': None,
    'last_scan_cold': None,
    'last_scan_hyderabad': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Header
st.title("🎯 Pranjal's AI Outreach Engine")
st.caption("Zero noise. Only leads that pass Gemini's filter.")

# --- Environment Variable Check ---
gemini_key = os.getenv("GEMINI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

if not gemini_key:
    st.error("⚠️ **GEMINI_API_KEY** is not set! Go to Streamlit Cloud → Settings → Secrets and add it. AI scoring and message generation will NOT work.")
if not github_token:
    st.warning("⚠️ **GITHUB_TOKEN** is not set! GitHub scraping (Hyderabad, Internship, Cold Email tabs) will return 0 results. Add it in Streamlit Cloud Secrets.")

# Four tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💼 Freelance Leads",
    "🚀 Internship & Contract",
    "📧 Cold Email (Founders)",
    "🏙️ Hyderabad Stealth Hunter"
])

with tab1:
    from tabs.freelance_tab import render_freelance_tab
    render_freelance_tab()

with tab2:
    from tabs.internship_tab import render_internship_tab
    render_internship_tab()

with tab3:
    from tabs.cold_email_tab import render_cold_email_tab
    render_cold_email_tab()

with tab4:
    from tabs.hyderabad_tab import render_hyderabad_tab
    render_hyderabad_tab()
