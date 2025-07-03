import streamlit as st
from summarizer import summarize_dataset

st.title("📋 AI Summary Generator")

df = st.session_state.get("df")
if df is not None:
    if st.button("🧠 Generate Summary"):
        summary = summarize_dataset(df.head(7))
        st.session_state["summary"] = summary
        st.markdown(summary)
else:
    st.warning("Please upload a dataset first.")
