import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

st.set_page_config(page_title="Datalicious — AI Data Assistant", layout="centered")

# Theme toggle
theme = st.selectbox("🌓 Theme", ["Light", "Dark"], index=0)

def apply_theme(theme):
    if theme == "Dark":
        css = """
        <style>
        body, [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top left, #1a1a2e, #16213e) !important;
            color: #f0f0f0 !important;
        }
        .block-container {
            background-color: rgba(25, 25, 25, 0.95);
            border-radius: 20px;
            padding: 3rem 3rem;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
        }
        .stButton > button {
            background: linear-gradient(to right, #667eea, #764ba2);
            color: white !important;
            border-radius: 10px;
            padding: 10px 24px;
        }
        h1, h2, h3 { color: #ffa8a8 !important; text-align: center; }
        input, textarea, select, .stFileUploader > div {
            background-color: #2c2c54 !important; color: #fff !important; border: 1px solid #888 !important;
        }
        .stDataFrame div { color: #fff !important; }
        .chat-user, .chat-ai {
            padding: 12px; border-radius: 10px; margin: 10px 0;
        }
        .chat-user { background: #3e3e66; color: #fff; }
        .chat-ai { background: #4a4a72; color: #fff; }
        </style>
        """
    else:
        css = """
        <style>
        body, [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top left, #fdfbfb, #ebedee) !important;
            color: #111 !important;
        }
        .block-container {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 3rem 3rem;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
        }
        .stButton > button {
            background: linear-gradient(to right, #ff758c, #ff7eb3);
            color: white !important;
            border-radius: 10px;
            padding: 10px 24px;
        }
        h1, h2, h3 { color: #d63384 !important; text-align: center; }
        input, textarea, select, .stFileUploader > div {
            background-color: #fff !important; color: #111 !important; border: 1px solid #bbb !important;
        }
        .stDataFrame div { color: #111 !important; }
        .chat-user, .chat-ai {
            padding: 12px; border-radius: 10px; margin: 10px 0;
        }
        .chat-user { background: #d0f0fd; }
        .chat-ai { background: #ffe5f7; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

apply_theme(theme)
# App title and intro
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("""
Upload structured data, generate insights, visualize trends, and export them professionally.  
**Powered by Together AI + Figma**
""")
st.divider()

# File Upload
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
            css_class = "chat-user" if role == "user" else "chat-ai"
            st.markdown(f"<div class='{css_class}'><strong>{'You' if role == 'user' else 'AI'}:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚫 Error processing file: {e}")
else:
    st.info("Please upload a CSV file to get started.")

