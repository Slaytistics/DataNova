import streamlit as st
import pandas as pd
import requests
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column

# 🔐 Load API key from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# 🖥️ Streamlit App UI
st.set_page_config(page_title="AI Dataset Summary Chatbot", layout="centered")
st.title("📊 AI-Powered Dataset Chatbot (GPT-4 Style)")
st.markdown("Upload a CSV file and get a summary & chart using AI ✨")

# 📂 File Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📁 Preview of Dataset:")
        st.dataframe(df.head())

        # 🧠 GPT Summary
        if st.button("🧠 Generate GPT Summary"):
            with st.spinner("Talking to GPT..."):
                summary = summarize_dataset(df, OPENROUTER_API_KEY)
                st.success("✅ Summary Ready!")
                st.markdown(f"📋 **Summary**:\n\n{summary}")

        # 📊 Infographic
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()

        if numeric_columns:
            selected_column = st.selectbox("📊 Select numeric column to visualize:", numeric_columns)
            if selected_column:
                fig = plot_top_column(df, selected_column)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for chart generation.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("⬆️ Upload a CSV file to get started.")

