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

# Database client (cached singleton)
@st.cache_resource
def get_db():
    from database.db_client import DatabaseClient
    return DatabaseClient()

db = get_db()

# Header
st.title("🎯 Pranjal's AI Outreach Engine")
st.caption("Zero noise. Only leads that pass Gemini's filter.")

# Session state init
if 'scan_running' not in st.session_state:
    st.session_state.scan_running = False
if 'last_scan_hyderabad' not in st.session_state:
    st.session_state.last_scan_hyderabad = None

# Four tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💼 Freelance Leads",
    "🚀 Internship & Contract",
    "📧 Cold Email (Founders)",
    "🏙️ Hyderabad Stealth Hunter"
])

with tab1:
    from tabs.freelance_tab import render_freelance_tab
    render_freelance_tab(db)

with tab2:
    from tabs.internship_tab import render_internship_tab
    render_internship_tab(db)

with tab3:
    from tabs.cold_email_tab import render_cold_email_tab
    render_cold_email_tab(db)

with tab4:
    from tabs.hyderabad_tab import render_hyderabad_tab
    render_hyderabad_tab(db)
