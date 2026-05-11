import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_all_reports, get_stats, init_db, save_report
from extractor import extract_field_report
from rag import add_report_to_rag, query_agent

st.set_page_config(layout="wide", page_icon="🌍", page_title="FieldMind")
init_db()

st.title("FieldMind — Enterprise Field Intelligence Agent")
st.caption("Turning informal field reports into enterprise intelligence")

tab_submit, tab_agent, tab_dashboard, tab_all = st.tabs(
    ["📝 Submit Report", "🤖 Ask the Agent", "📊 Dashboard", "📋 All Reports"]
)

with tab_submit:
    st.subheader("Submit a Field Report")
    report_text = st.text_area("Paste raw field report", height=180)

    if st.button("Process Report"):
        if not report_text.strip():
            st.warning("Please enter a report before processing.")
        else:
            try:
                with st.spinner("Extracting intelligence from report..."):
                    extracted = extract_field_report(report_text)
                    report_id = save_report(extracted)
                    add_report_to_rag(str(report_id), extracted.get("summary", ""), extracted)
                st.success("Report processed and indexed successfully.")
                st.json(extracted)
            except Exception as error:
                st.warning(f"Could not process report: {error}")

with tab_agent:
    st.subheader("Ask FieldMind")
    question = st.text_input("Ask an operational question")
    if st.button("Ask Agent"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Analyzing indexed reports..."):
                    answer = query_agent(question)
                st.success("Analysis complete.")
                st.markdown(answer)
            except Exception as error:
                st.warning(f"Could not generate answer: {error}")

with tab_dashboard:
    st.subheader("Operational Dashboard")
    stats = get_stats()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reports", stats["total"])
    col2.metric("Action Needed", stats["action_needed"])
    col3.metric("High Urgency", stats["high_urgency"])
    col4.metric("Frustrated/Angry", stats["frustrated_or_angry"])

    reports = get_all_reports()
    if reports:
        df = pd.DataFrame(reports)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            sentiment_counts = df["sentiment"].value_counts().reset_index()
            sentiment_counts.columns = ["sentiment", "count"]
            sentiment_fig = px.pie(sentiment_counts, names="sentiment", values="count", title="Sentiment Distribution")
            st.plotly_chart(sentiment_fig, use_container_width=True)

        with chart_col2:
            issue_counts = df["issue_type"].value_counts().reset_index()
            issue_counts.columns = ["issue_type", "count"]
            issue_fig = px.bar(issue_counts, x="issue_type", y="count", title="Top Issue Types")
            st.plotly_chart(issue_fig, use_container_width=True)

        display_columns = ["location", "issue_type", "sentiment", "urgency", "summary"]
        st.dataframe(df[display_columns], use_container_width=True)
    else:
        st.warning("No reports available yet. Submit a report to populate the dashboard.")

with tab_all:
    st.subheader("All Reports")
    reports = get_all_reports()
    if not reports:
        st.warning("No reports found yet.")
    else:
        for report in reports:
            title = (
                f"{report.get('created_at', 'Unknown time')} — "
                f"{report.get('agent_name', 'Unknown agent')} ({report.get('location', 'Unknown location')})"
            )
            with st.expander(title):
                st.markdown(f"**Issue Type:** {report.get('issue_type', 'N/A')}")
                st.markdown(f"**Urgency:** {report.get('urgency', 'N/A')} | **Sentiment:** {report.get('sentiment', 'N/A')}")
                st.markdown(f"**Summary:** {report.get('summary', '')}")
                st.markdown("**Raw Input:**")
                st.write(report.get("raw_input", ""))
