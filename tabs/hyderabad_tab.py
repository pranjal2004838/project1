import streamlit as st
from datetime import datetime
from utils.scan_runner import run_hyderabad_scan
from ai.hyderabad_scorer import generate_hyderabad_email

def render_hyderabad_tab(db):
    st.header("🏙️ Hyderabad Stealth Startup Hunter")
    st.caption(
        "Finds startups NOT on Internshala, LinkedIn, or Naukri. "
        "Sources: T-Hub directory, GitHub Hyderabad users, YourStory, Inc42, Product Hunt, domain scraping."
    )

    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    stats = db.get_hyderabad_stats()
    col1.metric("Total Discovered", stats['total'])
    col2.metric("Passed Filter", stats['passed'])
    col3.metric("Emails Drafted", stats['drafted'])
    col4.metric("Replies Received", stats['replied'])

    # Scan control
    st.divider()
    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Hyderabad Scan", disabled=st.session_state.scan_running, type="primary"):
            st.session_state.scan_running = True
            with st.spinner("Scanning Hyderabad sources and scoring with Gemini..."):
                found, passed = run_hyderabad_scan(db)
                st.session_state.last_scan_hyderabad = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} ({found} found, {passed} passed)"
            st.session_state.scan_running = False
            st.rerun()
        
        st.caption("Sources: T-Hub · GitHub · YourStory · Inc42 · Product Hunt")

    with col_status:
        if st.session_state.last_scan_hyderabad:
            st.info(f"Last scan: {st.session_state.last_scan_hyderabad}")

    # Filters
    st.divider()
    with st.expander("🔽 Filters", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        source_filter = f_col1.multiselect(
            "Source", ["thub", "github", "yourstory", "inc42", "product_hunt", "domain"], default=[]
        )
        stack_filter = f_col2.multiselect(
            "Stack Match", ["React", "Flutter", "Firebase", "Node.js", "Python", "TypeScript"], default=[]
        )
        status_filter = f_col3.multiselect(
            "Status", ["new", "drafted", "sent", "replied", "interested", "closed"], default=["new", "drafted"]
        )
        min_score = 0 # Forced to 0 to show all

    # Startup cards
    startups = db.get_hyderabad_startups(
        sources=source_filter,
        statuses=status_filter,
        min_score=min_score
    )

    if not startups:
        st.info("No startups match your filters. Run a scan or adjust filters.")
        return

    for startup in startups:
        render_hyderabad_card(startup, db)


def render_hyderabad_card(startup: dict, db):
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            # Header
            source_colors = {
                'thub': '🏛️', 'github': '⚫', 'yourstory': '📰',
                'inc42': '📊', 'product_hunt': '🐱', 'domain': '🌐'
            }
            icon = source_colors.get(startup['source'], '📍')
            st.markdown(f"### {icon} {startup['company_name']}")

            if startup.get('founder_name'):
                st.caption(f"Founder: **{startup['founder_name']}**")

            # Description
            if startup.get('description'):
                desc = startup['description']
                st.write(desc[:200] + ('...' if len(desc) > 200 else ''))

            # Stack tags
            if startup.get('tech_stack'):
                import json
                try:
                    stack = json.loads(startup['tech_stack']) if isinstance(startup['tech_stack'], str) else startup['tech_stack']
                except:
                    stack = []
                pranjal_stack = {'React', 'Flutter', 'Firebase', 'Node.js', 'TypeScript', 'Supabase', 'MongoDB'}
                tags = " ".join([
                    f"**`{s}`**" if s in pranjal_stack else f"`{s}`"
                    for s in stack[:8]
                ])
                st.markdown(f"Stack: {tags}")

            # Activity signal
            if startup.get('activity_signal'):
                st.caption(f"⏱️ {startup['activity_signal']}")

            # Fit reason
            if startup.get('fit_reason'):
                st.success(f"**AI Opinion:** {startup['fit_reason']}")

        with col2:
            # Score badge & Classification
            score = startup.get('score', 0)
            if score >= 85:
                classification = "Definitely Best Opportunity"
            elif score >= 70:
                classification = "Good Fit"
            elif score >= 50:
                classification = "Maybe"
            else:
                classification = "Waste of Time"
                
            st.metric("Classification", classification, delta=f"Score: {score}", delta_color="off")

            # Status dropdown
            status_options = ["new", "drafted", "sent", "replied", "interested", "closed"]
            current_status = startup.get('status', 'new')
            if current_status not in status_options:
                current_status = 'new'
                
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status),
                key=f"status_{startup['id']}"
            )
            if new_status != startup.get('status'):
                db.update_hyderabad_status(startup['id'], new_status)
                st.rerun()

        # Links row
        link_col1, link_col2, link_col3 = st.columns(3)
        if startup.get('company_url'):
            link_col1.markdown(f"[🌐 Website]({startup['company_url']})")
        if startup.get('github_url'):
            link_col2.markdown(f"[⚫ GitHub]({startup['github_url']})")
        if startup.get('email'):
            link_col3.markdown(f"📧 `{startup['email']}`")

        # Email section
        with st.expander("📧 View / Generate Email"):
            if startup.get('generated_message'):
                st.text_input("Subject", value=startup.get('generated_subject', ''), key=f"subj_{startup['id']}")
                edited_msg = st.text_area(
                    "Email Body",
                    value=startup['generated_message'],
                    height=200,
                    key=f"msg_{startup['id']}"
                )
                col_copy, col_regen = st.columns(2)
                if col_copy.button("📋 Copy Email", key=f"copy_{startup['id']}"):
                    st.code(f"Subject: {startup.get('generated_subject','')}\n\n{edited_msg}")
                    st.toast("Copied! Paste into your email client.")
                if col_regen.button("🔄 Regenerate", key=f"regen_{startup['id']}"):
                    with st.spinner("Regenerating with Gemini..."):
                        email_data = generate_hyderabad_email(startup)
                        db.save_hyderabad_email(startup['id'], email_data.get('subject', ''), email_data.get('message', ''))
                    st.rerun()
            else:
                if st.button("✨ Generate Email Now", key=f"gen_{startup['id']}"):
                    with st.spinner("Generating with Gemini..."):
                        email_data = generate_hyderabad_email(startup)
                        db.save_hyderabad_email(startup['id'], email_data.get('subject', ''), email_data.get('message', ''))
                    st.rerun()

        # Notes field
        notes = st.text_input(
            "Your notes (visible only to you)",
            value=startup.get('notes', ''),
            key=f"notes_{startup['id']}",
            placeholder="e.g. Met founder at T-Hub event, follow up on Monday"
        )
        if notes != startup.get('notes', ''):
            db.update_hyderabad_notes(startup['id'], notes)
