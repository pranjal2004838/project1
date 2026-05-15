import streamlit as st
import json
import time
from scrapers.hyderabad.github_hyd_scraper import search_hyderabad_github_users, format_github_user_as_startup
from scrapers.hyderabad.search_hyd_scraper import search_hyderabad_startups
from scrapers.linkedin_scraper import search_linkedin_leads
from ai.hyderabad_scorer import score_hyderabad_startup, generate_hyderabad_email

def get_classification(score):
    if score >= 85: return "🏆 Definitely Best Opportunity"
    elif score >= 70: return "✅ Good Fit"
    elif score >= 50: return "🤔 Maybe"
    else: return "❌ Waste of Time"

def run_hyderabad_scan():
    """Runs the scan and stores results in session_state."""
    all_results = []
    
    progress = st.progress(0, text="Searching GitHub for Hyderabad founders...")
    try:
        github_users = search_hyderabad_github_users()
        github_startups = [format_github_user_as_startup(u) for u in github_users]
        all_results.extend(github_startups)
    except Exception as e:
        st.warning(f"GitHub search failed: {e}")

    progress.progress(0.2, text="Hunting for stealth startups via Search...")
    try:
        search_results = search_hyderabad_startups()
        all_results.extend(search_results)
    except Exception as e:
        print(f"Smart Search failed: {e}")
    
    progress.progress(0.3, text="Finding Hyderabad founders on LinkedIn...")
    try:
        linkedin_leads = search_linkedin_leads(query_type="hyderabad")
        for lead in linkedin_leads:
            all_results.append({
                "company_name": lead['name'],
                "description": lead['description'],
                "company_url": lead['url'],
                "source": "linkedin",
                "tech_stack": []
            })
    except Exception as e:
        print(f"LinkedIn search failed: {e}")
    
    results = []
    total = len(all_results)
    
    for i, startup in enumerate(all_results):
        try:
            progress.progress(0.3 + 0.7 * (i + 1) / max(total, 1), text=f"Scoring startup {i+1}/{total} with Gemini...")
            
            scoring_data = {
                "company_name": startup.get("company_name", "Unknown"),
                "source": startup.get("source", "unknown"),
                "description": startup.get("description", ""),
                "tech_stack": json.dumps(startup.get("tech_stack", [])),
                "company_size": startup.get("company_size", "unknown"),
                "last_activity": startup.get("last_activity", "unknown"),
                "company_url": startup.get("company_url", ""),
                "github_url": startup.get("github_url", ""),
                "fit_reason": "",  # placeholder for email template
                "urgency_signal": "",
            }
            
            analysis = score_hyderabad_startup(scoring_data)
            startup.update({
                "score": analysis.get("score", 0),
                "fit_reason": analysis.get("fit_reason", ""),
                "stack_overlap": analysis.get("stack_overlap", []),
                "urgency_signal": analysis.get("urgency_signal", ""),
                "disqualify_reason": analysis.get("disqualify_reason"),
            })
            
            # Auto-generate email — always, regardless of score
            scoring_data["fit_reason"] = startup["fit_reason"]
            scoring_data["urgency_signal"] = startup["urgency_signal"]
            email_data = generate_hyderabad_email(scoring_data)
            startup["generated_subject"] = email_data.get("subject", "")
            startup["generated_message"] = email_data.get("message", "")
            
            results.append(startup)
            if i < total - 1:
                time.sleep(4.1)
        except Exception as e:
            st.warning(f"Skipped one startup: {e}")
    
    progress.empty()
    st.session_state.hyderabad_startups = results
    st.session_state.last_scan_hyderabad = f"Found {len(results)} startups"


def render_hyderabad_tab():
    st.header("🏙️ Hyderabad Stealth Startup Hunter")
    st.caption("Finds startups NOT on Internshala, LinkedIn, or Naukri. Sources: T-Hub, GitHub Hyderabad.")

    # Stats row
    startups = st.session_state.hyderabad_startups
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Found", len(startups))
    col2.metric("High Opportunity (≥70)", sum(1 for s in startups if s.get("score", 0) >= 70))
    col3.metric("Maybe (50-69)", sum(1 for s in startups if 50 <= s.get("score", 0) < 70))
    col4.metric("Emails Ready", sum(1 for s in startups if s.get("generated_message")))

    st.divider()
    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Hyderabad Scan", type="primary", disabled=st.session_state.scan_running):
            st.session_state.scan_running = True
            run_hyderabad_scan()
            st.session_state.scan_running = False
            st.rerun()
        st.caption("Sources: GitHub · LinkedIn · Smart Search")
    with col_status:
        if st.session_state.last_scan_hyderabad:
            st.info(f"Last scan: {st.session_state.last_scan_hyderabad}")

    if not startups:
        st.info("No startups yet. Click **Run Hyderabad Scan** to start.")
        return

    st.divider()
    st.subheader(f"📋 {len(startups)} Startups Found — Sorted by Score")

    for i, startup in enumerate(sorted(startups, key=lambda x: x.get('score', 0), reverse=True)):
        score = startup.get('score', 0)
        classification = get_classification(score)
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                source_icons = {'thub': '🏛️', 'github': '⚫', 'search': '🔍'}
                icon = source_icons.get(startup.get('source', ''), '📍')
                st.markdown(f"### {icon} {startup.get('company_name', 'Unknown Startup')}")
                
                if startup.get('founder_name'):
                    st.caption(f"Founder: **{startup['founder_name']}**")
                
                if startup.get('description'):
                    st.write(startup['description'][:250] + "...")
                
                # Stack tags
                stack = startup.get('tech_stack', [])
                if isinstance(stack, str):
                    try: stack = json.loads(stack)
                    except: stack = []
                if stack:
                    pranjal_stack = {'React', 'Flutter', 'Firebase', 'Node.js', 'TypeScript', 'Supabase', 'MongoDB', 'JavaScript'}
                    tags = " · ".join([f"**{s}**" if s in pranjal_stack else s for s in stack[:6]])
                    st.caption(f"Stack: {tags}")
                
                if startup.get('activity_signal'):
                    st.caption(f"⏱️ {startup['activity_signal']}")
                
                if startup.get('fit_reason'):
                    st.success(f"**AI Opinion:** {startup['fit_reason']}")
                    
                if startup.get('disqualify_reason'):
                    st.warning(f"⚠️ Note: {startup['disqualify_reason']}")
            
            with col2:
                st.metric("Score", score)
                st.markdown(f"**{classification}**")
                if startup.get('stack_overlap'):
                    overlap = startup['stack_overlap']
                    if isinstance(overlap, list):
                        st.caption("Overlap: " + ", ".join(overlap[:3]))
            
            # Links
            link_cols = st.columns(3)
            if startup.get('company_url'):
                link_cols[0].markdown(f"[🌐 Website]({startup['company_url']})")
            if startup.get('github_url'):
                link_cols[1].markdown(f"[⚫ GitHub]({startup['github_url']})")
            
            # Email section
            if startup.get('generated_message'):
                with st.expander("📧 View Generated Email"):
                    st.text_input("Subject", value=startup.get('generated_subject', ''), key=f"hyd_subj_{i}")
                    st.text_area("Email Body", value=startup['generated_message'], height=200, key=f"hyd_msg_{i}")
                    if st.button("📋 Copy", key=f"hyd_copy_{i}"):
                        st.code(f"Subject: {startup.get('generated_subject','')}\n\n{startup['generated_message']}")
            else:
                if st.button("✨ Generate Email Now", key=f"hyd_gen_{i}"):
                    with st.spinner("Generating with Gemini..."):
                        scoring_data = {
                            "company_name": startup.get("company_name", ""),
                            "description": startup.get("description", ""),
                            "tech_stack": json.dumps(startup.get("tech_stack", [])),
                            "fit_reason": startup.get("fit_reason", ""),
                            "urgency_signal": startup.get("urgency_signal", ""),
                            "company_url": startup.get("company_url", ""),
                            "github_url": startup.get("github_url", ""),
                        }
                        email_data = generate_hyderabad_email(scoring_data)
                        st.session_state.hyderabad_startups[i]["generated_subject"] = email_data.get("subject", "")
                        st.session_state.hyderabad_startups[i]["generated_message"] = email_data.get("message", "")
                    st.rerun()
