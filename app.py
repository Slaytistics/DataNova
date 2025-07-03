import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# Page configuration
st.set_page_config(page_title="Datalicious — AI Data Assistant", layout="wide")

# Custom Styling for Interactivity and Aesthetic Appeal
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://i.imgur.com/qo8IZvH.jpeg");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: Arial, italic;
    }

    .block-container {
        background: rgba(255, 255, 255, 0.8);
        padding: 2rem 3rem;
        border-radius: 16px;
        max-width: 1000px;
        margin: auto;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }

    input, textarea, select, .stFileUploader > div {
        background-color: rgba(255,255,255,0.95) !important;
        border-radius: 10px;
        padding: 10px;
        font-family: Arial, italic;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff69b4, #ff1493);
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        padding: 12px 30px;
        box-shadow: 0 4px 10px rgba(255, 20, 147, 0.6);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #ff1493, #ff69b4);
        box-shadow: 0 6px 14px rgba(255, 20, 147, 0.8);
    }

    h1, .stTitle { color: #FF69B4; }
    h2, .stHeader { color: #FF0000; }
    h3 { color: #0000FF; }
    h4 { color: #FF00FF; }
    h5 { color: #800080; }
    h6 { color: #C71585; }

    .chat-user, .chat-ai {
        background: #fff;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-style: italic;
    }
    .chat-user { background: #FFE4E1; }
    .chat-ai { background: #F0F8FF; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and Intro
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("""
Welcome to **Datalicious**! 🎉 Upload a CSV file to:
- 🔍 Explore and summarize your data
- 📈 Generate insightful charts
- 💬 Ask AI questions about your dataset
- 🎨 Export summaries to **Figma**
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

