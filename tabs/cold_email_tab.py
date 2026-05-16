import streamlit as st
import time
from scrapers.github_org_scraper import search_small_orgs_and_founders
from scrapers.linkedin_scraper import search_linkedin_leads
from ai.cold_email_scorer import score_cold_email_target, generate_founder_cold_email

def get_classification(score):
    if score >= 85: return "🏆 Definitely Best Opportunity"
    elif score >= 70: return "✅ Good Fit"
    elif score >= 50: return "🤔 Maybe"
    else: return "❌ Waste of Time"

def run_cold_email_scan():
    """Runs the scan and stores results in session_state."""
    progress = st.progress(0, text="Searching GitHub for global founders...")
    github_founders = search_small_orgs_and_founders(query_term="founder")

    progress.progress(0.3, text="Searching LinkedIn for active founders...")
    linkedin_leads = search_linkedin_leads(query_type="founder")

    # Format LinkedIn results
    linkedin_founders = []
    for lead in linkedin_leads:
        linkedin_founders.append({
            "name": lead['name'],
            "company": lead['title'],
            "founder_name": lead['name'],
            "company_name": lead['title'] or lead['name'],
            "description": lead['description'],
            "url": lead['url'],           # This is now a proper LinkedIn URL
            "linkedin_url": lead.get('linkedin_url', lead['url']),
            "source": "linkedin",
            "activity_signal": "Active on LinkedIn",
            "tech_stack": "",
            "company_size": "small",
        })

    raw_targets = github_founders + linkedin_founders
    results = []

    for i, target in enumerate(raw_targets):
        try:
            progress.progress((i + 1) / max(len(raw_targets), 1), text=f"Scoring target {i+1}/{len(raw_targets)}...")
            
            # Prepare scoring data
            score_data = {
                "founder_name": target.get("founder_name", target.get("name", "Unknown")),
                "company_name": target.get("company_name", target.get("company", "Unknown Company")),
                "tech_stack": target.get("stack", target.get("tech_stack", "")),
                "company_size": target.get("company_size", "small startup"),
                "activity_signal": target.get("activity_signal", "Active developer"),
            }
            analysis = score_cold_email_target(score_data)
            
            target.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "founder_name": score_data["founder_name"],
                "company_name": score_data["company_name"],
                "tech_stack": score_data["tech_stack"],
                "activity_signal": score_data["activity_signal"],
            })
            
            # Auto-generate email
            email_data = generate_founder_cold_email(score_data)
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
    st.caption("Finds tech founders globally and writes confident peer-to-peer emails. Shows LinkedIn profiles — not GitHub.")

    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Global Founder Scan", type="primary", disabled=st.session_state.scan_running):
            st.session_state.scan_running = True
            run_cold_email_scan()
            st.session_state.scan_running = False
            st.rerun()
        st.caption("Sources: GitHub Founders · LinkedIn Founders")
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
                if target.get('tech_stack'):
                    st.caption(f"Stack: {target['tech_stack']}")
                if target.get('fit_reason'):
                    st.success(f"**AI Opinion:** {target['fit_reason']}")
                if target.get('activity_signal'):
                    st.info(f"⚡ {target['activity_signal']}")
                if target.get('description'):
                    st.write(target['description'][:250])
            with col2:
                st.metric("Score", score)
                st.markdown(f"**{classification}**")

            # Show LinkedIn link preferentially
            linkedin_url = target.get('linkedin_url') or target.get('url', '')
            github_url = target.get('github_url', '')
            link_cols = st.columns(3)
            if linkedin_url and "linkedin.com" in linkedin_url:
                link_cols[0].markdown(f"[🔗 LinkedIn Profile]({linkedin_url})")
            elif target.get('url'):
                link_cols[0].markdown(f"[🔗 View Profile]({target['url']})")
            if github_url:
                link_cols[1].markdown(f"[⚫ GitHub]({github_url})")

            if target.get('generated_message'):
                with st.expander("📧 View Generated Email"):
                    st.text_input("Subject", value=target.get('generated_subject', ''), key=f"ce_subj_{i}")
                    st.text_area("Email Body", value=target['generated_message'], height=150, key=f"ce_msg_{i}")
            else:
                if st.button("✨ Generate Email Now", key=f"ce_gen_{i}"):
                    with st.spinner("Generating email with Gemini..."):
                        score_data = {
                            "founder_name": target.get("founder_name", "Founder"),
                            "company_name": target.get("company_name", "Company"),
                            "tech_stack": target.get("tech_stack", ""),
                            "activity_signal": target.get("activity_signal", ""),
                        }
                        email_data = generate_founder_cold_email(score_data)
                        subject = email_data.get("subject", "")
                        message = email_data.get("message", "")
                        if not message:
                            message = "Could not generate email — check GEMINI_API_KEY in Streamlit secrets."
                        st.session_state.cold_email_targets[i]["generated_subject"] = subject
                        st.session_state.cold_email_targets[i]["generated_message"] = message
                    st.rerun()
