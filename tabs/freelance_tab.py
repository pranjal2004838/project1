import streamlit as st
from datetime import datetime

def render_freelance_tab(db):
    st.header("💼 Freelance Leads")
    st.caption("Scrapes Reddit, HN, etc. for immediate high-intent freelance gigs.")

    # Scan control
    st.divider()
    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Freelance Scan", type="primary"):
            st.info("Scan started in background...")
            # Note: actual scan logic would be imported and called here
        
        st.caption("Sources: Reddit · HackerNews · IndieHackers")

    # Filters
    st.divider()
    with st.expander("🔽 Filters", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        status_filter = f_col1.multiselect(
            "Status", ["new", "contacted", "replied", "closed"], default=["new"]
        )
        min_score = f_col2.slider("Min Score (Freelance)", 0, 100, 72)

    # Fetch from DB (assuming db_client has a get_leads method)
    # Since we haven't implemented get_leads yet, we'll add a placeholder or simple query
    try:
        query = "SELECT * FROM leads WHERE score >= ?"
        params = [min_score]
        if status_filter:
            query += f" AND status IN ({','.join(['?' for _ in status_filter])})"
            params.extend(status_filter)
        query += " ORDER BY score DESC LIMIT 50"
        
        leads = db.execute_query(query, params)
        leads = [dict(row) for row in leads]
    except Exception as e:
        st.error(f"Error fetching leads: {e}")
        leads = []

    if not leads:
        st.info("No leads match your filters. Run a scan or adjust filters.")
        return

    for lead in leads:
        render_freelance_card(lead, db)


def render_freelance_card(lead: dict, db):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### [{lead['platform'].upper()}] {lead['title']}")
            if lead.get('channel'):
                st.caption(f"Channel: **{lead['channel']}** | Posted: {lead.get('posted_at', '')[:10]}")
            
            # Pain point & Service
            if lead.get('pain_point'):
                st.warning(f"**Pain Point:** {lead['pain_point']}")
            if lead.get('service_match'):
                st.success(f"**Match:** {lead['service_match']}")
                
            # Body snippet
            if lead.get('body'):
                st.write(lead['body'][:300] + "...")

        with col2:
            # Score badge
            score = lead.get('score', 0)
            st.metric("Score", f"{score}", delta=lead.get('urgency', 'medium'))

            # Status dropdown
            status_options = ["new", "contacted", "replied", "closed"]
            current_status = lead.get('status', 'new')
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 0,
                key=f"f_status_{lead['id']}"
            )
            if new_status != current_status:
                db.execute_query("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead['id']), commit=True)
                st.rerun()

        # Links & Message
        st.markdown(f"[🌐 Original Post]({lead['url']})")
        
        with st.expander("💬 View / Draft Message"):
            if lead.get('generated_message'):
                st.text_area("Generated Message", value=lead['generated_message'], height=150, key=f"f_msg_{lead['id']}")
            else:
                if st.button("✨ Generate Reply", key=f"f_gen_{lead['id']}"):
                    st.info("Message generation logic would run here.")
