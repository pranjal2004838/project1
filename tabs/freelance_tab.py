import streamlit as st
import time
from scrapers.reddit_scraper import scrape_reddit_leads
from scrapers.linkedin_scraper import search_linkedin_leads
from ai.freelance_scorer import score_freelance_lead, generate_freelance_message

def run_freelance_scan():
    """Runs the scan and stores results in session_state."""
    st.session_state.freelance_leads = []
    raw_leads = scrape_reddit_leads()
    results = []
    
    progress = st.progress(0, text="Scraping Reddit and HackerNews...")
    reddit_leads = scrape_reddit_leads()
    
    progress.progress(0.2, text="Searching LinkedIn for freelance posts...")
    linkedin_leads = search_linkedin_leads(query_type="freelance")
    
    raw_leads = reddit_leads + linkedin_leads
        try:
            progress.progress((i + 1) / max(len(raw_leads), 1), text=f"Scoring lead {i+1}/{len(raw_leads)} with Gemini...")
            analysis = score_freelance_lead(lead)
            lead.update({
                "score": analysis.get("score", 0),
                "service_match": analysis.get("service_match", ""),
                "urgency": analysis.get("urgency", "low"),
                "hidden_pain": analysis.get("hidden_pain", ""),
                "fit_reason": analysis.get("fit_reason", ""),
            })
            # Auto-generate message
            msg_data = generate_freelance_message(lead)
            lead["generated_message"] = msg_data.get("message", "")
            results.append(lead)
            if i < len(raw_leads) - 1:
                time.sleep(4.1)
        except Exception as e:
            st.warning(f"Skipped one lead: {e}")
            
    progress.empty()
    st.session_state.freelance_leads = results
    st.session_state.last_scan_freelance = f"Found {len(results)} leads"

def get_classification(score):
    if score >= 85: return "🏆 Definitely Best Opportunity"
    elif score >= 70: return "✅ Good Fit"
    elif score >= 50: return "🤔 Maybe"
    else: return "❌ Waste of Time"

def render_freelance_tab():
    st.header("💼 Freelance Leads")
    st.caption("Scrapes Reddit for immediate high-intent freelance gigs and scores them with Gemini.")

    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Freelance Scan", type="primary", disabled=st.session_state.scan_running):
            st.session_state.scan_running = True
            run_freelance_scan()
            st.session_state.scan_running = False
            st.rerun()
        st.caption("Sources: Reddit · HackerNews · LinkedIn Search")
    with col_status:
        if st.session_state.last_scan_freelance:
            st.info(f"Last scan: {st.session_state.last_scan_freelance}")

    leads = st.session_state.freelance_leads
    
    if not leads:
        st.info("No leads yet. Click **Run Freelance Scan** to start.")
        return
    
    st.divider()
    st.subheader(f"📋 {len(leads)} Leads Found")

    for i, lead in enumerate(sorted(leads, key=lambda x: x.get('score', 0), reverse=True)):
        score = lead.get('score', 0)
        classification = get_classification(score)
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {lead.get('title', 'Untitled')}")
                st.caption(f"**{lead.get('channel', '')}** · {lead.get('posted_at', '')[:10]}")
                if lead.get('hidden_pain'):
                    st.warning(f"**Hidden Pain Detected:** {lead['hidden_pain']}")
                if lead.get('fit_reason') or lead.get('service_match'):
                    st.success(f"**AI Opinion:** {lead.get('fit_reason') or lead.get('service_match')}")
                if lead.get('body'):
                    st.write(lead['body'][:350] + "...")
            with col2:
                st.metric("Score", score)
                st.markdown(f"**{classification}**")
            
            st.markdown(f"[🔗 View Post]({lead.get('url', '#')})")
            
            if lead.get('generated_message'):
                with st.expander("💬 View Generated Message"):
                    st.text_area("Message", value=lead['generated_message'], height=150, key=f"fl_msg_{i}")
