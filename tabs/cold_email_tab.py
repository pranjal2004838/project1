import streamlit as st

def render_cold_email_tab(db):
    st.header("📧 Cold Email (Founders)")
    st.caption("Finds tech founders globally and writes confident peer-to-peer emails.")

    # Scan control
    st.divider()
    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Global Founder Scan", type="primary"):
            st.info("Scan started in background...")
        
        st.caption("Sources: GitHub · Wellfound · Product Hunt")

    # Filters
    st.divider()
    with st.expander("🔽 Filters", expanded=True):
        f_col1, f_col2 = st.columns(2)
        status_filter = f_col1.multiselect(
            "Status", ["new", "sent", "replied", "interested", "closed"], default=["new"]
        )
        min_score = f_col2.slider("Min Score (Founders)", 0, 100, 75)

    # Fetch from DB
    try:
        query = "SELECT * FROM cold_emails WHERE score >= ?"
        params = [min_score]
        if status_filter:
            query += f" AND status IN ({','.join(['?' for _ in status_filter])})"
            params.extend(status_filter)
        query += " ORDER BY score DESC LIMIT 50"
        
        targets = db.execute_query(query, params)
        targets = [dict(row) for row in targets]
    except Exception as e:
        st.error(f"Error fetching cold email targets: {e}")
        targets = []

    if not targets:
        st.info("No founders match your filters.")
        return

    for target in targets:
        render_cold_email_card(target, db)


def render_cold_email_card(target: dict, db):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### {target.get('founder_name', 'Founder')} @ {target.get('company_name', 'Company')}")
            
            if target.get('tech_stack'):
                st.caption(f"Stack: {target['tech_stack']}")
                
            if target.get('fit_reason'):
                st.success(f"**Fit:** {target['fit_reason']}")

        with col2:
            score = target.get('score', 0)
            st.metric("Score", f"{score}")

            status_options = ["new", "sent", "replied", "interested", "closed"]
            current_status = target.get('status', 'new')
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 0,
                key=f"c_status_{target['id']}"
            )
            if new_status != current_status:
                db.execute_query("UPDATE cold_emails SET status = ? WHERE id = ?", (new_status, target['id']), commit=True)
                st.rerun()

        with st.expander("📧 View / Draft Email"):
            if target.get('generated_message'):
                st.text_input("Subject", value=target.get('generated_subject', ''), key=f"c_subj_{target['id']}")
                st.text_area("Email Body", value=target['generated_message'], height=150, key=f"c_msg_{target['id']}")
            else:
                if st.button("✨ Generate Email", key=f"c_gen_{target['id']}"):
                    st.info("Email generation logic would run here.")
