import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# --- Page Setup ---
st.set_page_config(page_title="Datalicious", page_icon="📊", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f6f9fc;
    }

    h1 {
        font-size: 2.4rem;
        color: #1E2B3C;
    }

    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #004999;
        transform: scale(1.02);
    }

    .card {
        background-color: white;
        border-radius: 12px;
        padding: 25px 30px;
        margin-bottom: 30px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
    }

    .chat-user, .chat-ai {
        background-color: #eef2f6;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 6px 0;
        font-size: 15px;
    }

    .chat-ai {
        background-color: #fdf4f5;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title & Intro ---
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Smartly explore, summarize, and visualize CSV datasets — powered by GPT + Figma + Streamlit.")

# --- File Upload ---
st.markdown("### 📁 Upload Your Dataset")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # --- Data Preview ---
        st.markdown("### 🔍 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # --- Summary Section ---
        st.markdown("### 🧠 Smart Summary")
        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Analyzing data with GPT..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary generated successfully!")
        with col2:
            st.markdown("The AI summarizes your dataset's first few rows.")

        if summary:
            st.markdown("#### 📌 Summary Output:")
            st.markdown(summary)
            st.code(summary, language="text")

        # --- Chart Section ---
        st.markdown("### 📊 Chart Generator")
        numeric_columns = df.select_dtypes(include=["int", "float"]).columns.tolist()
        if numeric_columns:
            with st.expander("Chart Settings"):
                selected_column = st.selectbox("Choose numeric column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charting.")

        # --- Export Section ---
        if summary:
            st.markdown("### 📤 Export Summary (Simulated)")
            if st.button("Export to Figma (Simulated)"):
                with st.spinner("Preparing downloadable summary..."):
                    result = export_to_figma(summary)
                    st.success("Summary ready for export!")
                    st.markdown(result, unsafe_allow_html=True)

        # --- Q&A Section ---
        st.markdown("### ❓ Ask About This Dataset")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your Question:", placeholder="e.g. What's the most common value?")

        if user_input:
            with st.spinner("Thinking..."):
                reply = ask_dataset_question(df, user_input, mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        for role, msg in st.session_state.chat_history:
            css_class = "chat-user" if role == "user" else "chat-ai"
            st.markdown(f"<div class='{css_class}'><strong>{'You' if role == 'user' else 'AI'}:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📌 Please upload a CSV file to begin.")

