import streamlit as st

def render_internship_tab(db):
    st.header("🚀 Internship & Contract")
    st.caption("Finds small agencies and founders actively building who need a dev for 2 months.")

    # Scan control
    st.divider()
    col_scan, col_status = st.columns([2, 3])
    with col_scan:
        if st.button("🔍 Run Internship Scan", type="primary"):
            st.info("Scan started in background...")
        
        st.caption("Sources: GitHub Orgs · Wellfound · IndieHackers")

    # Filters
    st.divider()
    with st.expander("🔽 Filters", expanded=True):
        f_col1, f_col2 = st.columns(2)
        status_filter = f_col1.multiselect(
            "Status", ["new", "sent", "replied", "closed"], default=["new"]
        )
        min_score = 0 # Forced to 0 to show all

    # Fetch from DB
    try:
        query = "SELECT * FROM opportunities WHERE score >= ?"
        params = [min_score]
        if status_filter:
            query += f" AND status IN ({','.join(['?' for _ in status_filter])})"
            params.extend(status_filter)
        query += " ORDER BY score DESC LIMIT 100"
        
        opps = db.execute_query(query, params)
        opps = [dict(row) for row in opps]
    except Exception as e:
        st.error(f"Error fetching opportunities: {e}")
        opps = []

    if not opps:
        st.info("No opportunities match your filters.")
        return

    for opp in opps:
        render_internship_card(opp, db)


def render_internship_card(opp: dict, db):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### {opp.get('company', 'Unknown Company')} - {opp.get('name', 'Role')}")
            st.caption(f"Source: **{opp.get('source', '')}**")
            
            if opp.get('fit_reason'):
                st.success(f"**Fit:** {opp['fit_reason']}")
                
            if opp.get('description'):
                st.write(opp['description'][:300] + "...")

        with col2:
            score = opp.get('score', 0)
            if score >= 85:
                classification = "Definitely Best Opportunity"
            elif score >= 70:
                classification = "Good Fit"
            elif score >= 50:
                classification = "Maybe"
            else:
                classification = "Waste of Time"
                
            st.metric("Classification", classification, delta=f"Score: {score}", delta_color="off")

            status_options = ["new", "sent", "replied", "closed"]
            current_status = opp.get('status', 'new')
            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 0,
                key=f"i_status_{opp['id']}"
            )
            if new_status != current_status:
                db.execute_query("UPDATE opportunities SET status = ? WHERE id = ?", (new_status, opp['id']), commit=True)
                st.rerun()

        st.markdown(f"[🌐 Link to Opportunity]({opp.get('url', '#')})")
