import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# Page configuration
st.set_page_config(page_title="Datalicious — AI Data Assistant", layout="wide")

# Theme toggle
theme = st.selectbox("🌓 Choose Theme", ["Light", "Dark"], index=0)

# CSS Theme Styling
def apply_theme(theme):
    if theme == "Dark":
        css = """
        <style>
        body, [data-testid="stAppViewContainer"] {
            background: #1e1e1e !important;
            color: #f0f0f0 !important;
        }
        .block-container {
            background: rgba(30, 30, 30, 0.85) !important;
            border-radius: 16px;
            padding: 2rem 3rem;
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        }
        .stButton > button {
            background: linear-gradient(to right, #4e54c8, #8f94fb);
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ff69b4 !important;
        }
        input, textarea, select, .stFileUploader > div {
            background-color: #333 !important;
            color: #fff !important;
            border: 1px solid #888 !important;
        }
        .stDataFrame div {
            color: #fff !important;
        }
        .chat-user { background: #2c2c2c; color: #fff; }
        .chat-ai { background: #3a3a3a; color: #fff; }
        </style>
        """
    else:
        css = """
        <style>
        body, [data-testid="stAppViewContainer"] {
            background: #f9f9f9 !important;
            color: #111 !important;
        }
        .block-container {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 16px;
            padding: 2rem 3rem;
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background: linear-gradient(to right, #ff69b4, #ff1493);
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #cc0077 !important;
        }
        input, textarea, select, .stFileUploader > div {
            background-color: #fff !important;
            color: #111 !important;
            border: 1px solid #bbb !important;
        }
        .stDataFrame div {
            color: #111 !important;
        }
        .chat-user { background: #e0f7fa; }
        .chat-ai { background: #fce4ec; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

apply_theme(theme)

# Title & Intro
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("""
Upload structured data, generate insights, visualize trends, and export them professionally.  
**Powered by Together AI + Figma**
""")
st.divider()

# Upload Section
st.header("📁 Upload Your Dataset")
uploaded_file = st.file_uploader("Choose a CSV file to begin:", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("👀 Preview of Your Data")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("🧠 Generate Summary")
        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✨ Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated!")
        with col2:
            st.markdown("This summary gives a quick GPT-style insight into your dataset sample.")

        if summary:
            st.markdown(f"#### 📜 Summary Output\n{summary}")

        st.divider()
        st.header("📊 Chart Generator")

        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("🔧 Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose a numeric column to visualize:", numeric_columns)
                top_n = st.slider("Select Top N Values:", 5, 20, 10)

                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found in your dataset for charting.")

        st.divider()
        st.header("📤 Export to Figma")
        if summary:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("🚀 Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(summary, dataset_name=dataset_name)
                    st.toast("✅ Exported to Figma!")
                    st.success(result)

        st.divider()
        st.header("💬 Ask About This Dataset")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Type your question here:", placeholder="e.g. Which country has highest population?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚫 Error processing file: {e}")
else:
    st.info("Please upload a CSV file to get started.")



