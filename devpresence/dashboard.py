from pathlib import Path

import pandas as pd
import streamlit as st

from ai.content_generator import generate_content
from ai.tone_manager import get_unique_tone
from database import Opportunity, Post, SessionLocal
from lead_finder import OUTPUT_FILE, run_lead_research

st.set_page_config(page_title="DevPresence Dashboard", layout="wide", page_icon="🚀")

page = st.sidebar.radio("Navigation", ["Overview", "Opportunity Feed", "Content Generator", "Content Calendar", "Analytics"])
st.sidebar.divider()
st.sidebar.caption("Run a fresh public-web lead search and rewrite leads_found.txt each time.")


def load_data():
    session = SessionLocal()
    opps = session.query(Opportunity).all()
    posts = session.query(Post).all()
    session.close()
    return opps, posts


def render_lead_table(results):
    if not results:
        st.warning("No high-confidence leads were found in this run.")
        return

    frame = pd.DataFrame(results)
    display_columns = [column for column in ["score", "source", "category", "title", "url", "reason"] if column in frame.columns]
    st.dataframe(frame[display_columns], use_container_width=True, hide_index=True)
    for result in results:
        st.markdown(f"- [{result.get('title') or result['url']}]({result['url']})")


if st.sidebar.button("Run Lead Research", type="primary"):
    with st.spinner("Searching Reddit, LinkedIn, Discord, Slack, and the wider web..."):
        lead_results = run_lead_research()
    st.success(f"Saved {len(lead_results)} leads to {OUTPUT_FILE}")
    render_lead_table(lead_results)

if page == "Overview":
    st.title("🚀 DevPresence Dashboard")
    opps, posts = load_data()

    col1, col2, col3 = st.columns(3)
    col1.metric("Opportunities Found", len(opps))
    col2.metric("Posts Made", len(posts))
    col3.metric("Responses Sent", len([o for o in opps if o.responded]))
    st.info("Use the sidebar button to run the lead search and refresh the output file.")

elif page == "Opportunity Feed":
    st.title("🎯 Opportunity Feed")
    opps, _ = load_data()

    if not opps:
        st.info("No opportunities found yet. Run the scanner.")
    else:
        for opp in sorted(opps, key=lambda x: x.found_at, reverse=True):
            with st.expander(f"[{opp.platform.upper()}] {opp.title}"):
                st.write(f"**Author:** {opp.author} | **Found:** {opp.found_at}")
                st.text(opp.body)
                st.markdown(f"[Link to post]({opp.url})")

                if st.button(f"Generate Reply for #{opp.id}", key=f"gen_{opp.id}"):
                    tone = get_unique_tone(opp.platform, [])
                    with st.spinner("Generating with Gemini..."):
                        reply = generate_content(
                            platform=opp.platform,
                            context=f"{opp.title}\n{opp.body}",
                            content_type="comment_reply",
                            tone=tone,
                        )
                    st.success("Draft generated!")
                    st.text_area("AI Draft", reply, height=150)
                    if st.button("🚀 Post Now (Dry Run)"):
                        st.info("Marking as responded...")
                        session = SessionLocal()
                        db_opp = session.query(Opportunity).get(opp.id)
                        db_opp.responded = True
                        session.commit()
                        st.success("Reply posted successfully!")

elif page == "Content Generator":
    st.title("✍️ Content Generator")
    platform = st.selectbox("Target Platform", ["linkedin", "reddit", "discord", "slack"])
    content_type = st.selectbox("Content Type", ["self_promo", "comment_reply", "cold_pitch", "value_post"])
    tone = st.selectbox("Tone", ["casual", "professional", "story", "direct", "humble_brag"])

    context = st.text_area("Context or prompt (What should it be about?)")

    if st.button("Generate Variations"):
        if context:
            st.info("Calling Gemini API...")
            try:
                res1 = generate_content(platform, context, content_type, tone)
                st.write("**Variation 1:**")
                st.info(res1)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please provide context.")

elif page == "Content Calendar":
    st.title("📅 Content Calendar")
    st.info("Coming soon: View and edit scheduled posts via APScheduler.")

elif page == "Analytics":
    st.title("📊 Analytics")
    st.info("Coming soon: View profile views, clicks, and engagement tracks.")

