import streamlit as st
import time
from scrapers.github_org_scraper import search_small_orgs_and_founders
from ai.cold_email_scorer import score_cold_email_target, generate_founder_cold_email

def get_classification(score):
    if score >= 85: return "🏆 Definitely Best Opportunity"
    elif score >= 70: return "✅ Good Fit"
    elif score >= 50: return "🤔 Maybe"
    else: return "❌ Waste of Time"

def run_cold_email_scan():
    """Runs the scan and stores results in session_state."""
    raw_targets = search_small_orgs_and_founders(query_term="founder")
    results = []
    
    progress = st.progress(0, text="Searching GitHub for founders...")

    for i, target in enumerate(raw_targets):
        try:
            progress.progress((i + 1) / max(len(raw_targets), 1), text=f"Scoring target {i+1}/{len(raw_targets)}...")
            analysis = score_cold_email_target(target)
            target.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "founder_name": target.get("founder_name", target.get("name", "Unknown")),
                "company_name": target.get("company", "Unknown Company"),
            })
            # Auto-generate email
            email_data = generate_founder_cold_email(target)
            target["generated_subject"] = email_data.get("subject", "")
            target["generated_message"] = email_data.get("message", "")
            results.append(target)
            if i < len(raw_targets) - 1:
                time.sleep(4.1)
        except Exception as e:
            st.warning(f"Skipped one: {e}")
            
    progress.empty()
    st.session_state.cold_email_targets = results
    st.session_state.last_scan_cold = f"Found {len(results)} targets"

def render_cold_email_tab():
    st.header("📧 Cold Email (Founders)")
    st.caption("Finds tech founders globally and writes confident peer-to-peer emails.")

    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Global Founder Scan", type="primary", disabled=st.session_state.scan_running):
            st.session_state.scan_running = True
            run_cold_email_scan()
            st.session_state.scan_running = False
            st.rerun()
        st.caption("Sources: GitHub Orgs & active founders")
    with col_status:
        if st.session_state.last_scan_cold:
            st.info(f"Last scan: {st.session_state.last_scan_cold}")

    targets = st.session_state.cold_email_targets

    if not targets:
        st.info("No founders yet. Click **Run Global Founder Scan** to start.")
        return

    st.divider()
    st.subheader(f"📋 {len(targets)} Founders Found")

    for i, target in enumerate(sorted(targets, key=lambda x: x.get('score', 0), reverse=True)):
        score = target.get('score', 0)
        classification = get_classification(score)
        
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {target.get('founder_name', target.get('name', 'Founder'))} @ {target.get('company_name', target.get('company', 'Company'))}")
                if target.get('stack'):
                    st.caption(f"Stack: {target['stack']}")
                if target.get('fit_reason'):
                    st.success(f"**AI Opinion:** {target['fit_reason']}")
                if target.get('activity_signal'):
                    st.info(f"⚡ {target['activity_signal']}")
            with col2:
                st.metric("Score", score)
                st.markdown(f"**{classification}**")
            
            st.markdown(f"[🔗 View Profile]({target.get('url', '#')})")
            
            if target.get('generated_message'):
                with st.expander("📧 View Generated Email"):
                    st.text_input("Subject", value=target.get('generated_subject', ''), key=f"ce_subj_{i}")
                    st.text_area("Email Body", value=target['generated_message'], height=150, key=f"ce_msg_{i}")
