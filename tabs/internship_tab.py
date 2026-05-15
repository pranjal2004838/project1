import streamlit as st
import time
from scrapers.github_org_scraper import search_small_orgs_and_founders
from ai.internship_scorer import score_internship_opportunity, generate_internship_email

def get_classification(score):
    if score >= 85: return "🏆 Definitely Best Opportunity"
    elif score >= 70: return "✅ Good Fit"
    elif score >= 50: return "🤔 Maybe"
    else: return "❌ Waste of Time"

def run_internship_scan():
    """Runs the scan and stores results in session_state."""
    raw_opps = search_small_orgs_and_founders(query_term="startup")
    results = []
    
    progress = st.progress(0, text="Searching GitHub for small tech teams...")

    for i, opp in enumerate(raw_opps):
        try:
            progress.progress((i + 1) / max(len(raw_opps), 1), text=f"Scoring opportunity {i+1}/{len(raw_opps)}...")
            analysis = score_internship_opportunity(opp)
            opp.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "urgency_signal": analysis.get("urgency_signal", ""),
            })
            # Auto-generate email
            email_data = generate_internship_email(opp)
            opp["generated_subject"] = email_data.get("subject", "")
            opp["generated_message"] = email_data.get("message", "")
            results.append(opp)
            if i < len(raw_opps) - 1:
                time.sleep(4.1)
        except Exception as e:
            st.warning(f"Skipped one: {e}")
            
    progress.empty()
    st.session_state.internship_opps = results
    st.session_state.last_scan_internship = f"Found {len(results)} opportunities"

def render_internship_tab():
    st.header("🚀 Internship & Contract")
    st.caption("Finds small agencies and founders actively building who need a developer for 2 months.")

    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Internship Scan", type="primary", disabled=st.session_state.scan_running):
            st.session_state.scan_running = True
            run_internship_scan()
            st.session_state.scan_running = False
            st.rerun()
        st.caption("Sources: GitHub Orgs & small teams")
    with col_status:
        if st.session_state.last_scan_internship:
            st.info(f"Last scan: {st.session_state.last_scan_internship}")

    opps = st.session_state.internship_opps
    
    if not opps:
        st.info("No opportunities yet. Click **Run Internship Scan** to start.")
        return

    st.divider()
    st.subheader(f"📋 {len(opps)} Opportunities Found")

    for i, opp in enumerate(sorted(opps, key=lambda x: x.get('score', 0), reverse=True)):
        score = opp.get('score', 0)
        classification = get_classification(score)
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {opp.get('company', 'Unknown Company')}")
                st.caption(f"Source: **{opp.get('source', '')}**")
                if opp.get('fit_reason'):
                    st.success(f"**AI Opinion:** {opp['fit_reason']}")
                if opp.get('urgency_signal'):
                    st.info(f"⚡ **Urgency:** {opp['urgency_signal']}")
                if opp.get('description'):
                    st.write(opp['description'][:300] + "...")
            with col2:
                st.metric("Score", score)
                st.markdown(f"**{classification}**")
            
            st.markdown(f"[🔗 View Company]({opp.get('url', '#')})")
            
            if opp.get('generated_message'):
                with st.expander("📧 View Generated Email"):
                    st.text_input("Subject", value=opp.get('generated_subject', ''), key=f"int_subj_{i}")
                    st.text_area("Email Body", value=opp['generated_message'], height=150, key=f"int_msg_{i}")
