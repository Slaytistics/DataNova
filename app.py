import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# ---------- THEME SELECTOR (Sidebar)
st.sidebar.title("🎨 Choose Theme")
theme = st.sidebar.selectbox("Select UI Theme", ["🔮 Neon Night", "🧊 Cool Light", "💼 Professional Blue"])

# ---------- THEME CSS Definitions
THEMES = {
    "🔮 Neon Night": """
        <style>
        body, html { background-color: #0f0f15 !important; font-family: 'Poppins', sans-serif; color: white !important; }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            min-height: 100vh;
            padding-top: 2rem;
        }
        .block-container {
            max-width: 900px;
            margin: auto;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            backdrop-filter: blur(16px);
            box-shadow: 0 0 20px 2px #ff69b4, 0 0 40px 6px #9b30ff;
            padding: 2rem 3rem;
        }
        h1, h2, h3 { color: #ff69b4 !important; }
        </style>
    """,
    "🧊 Cool Light": """
        <style>
        body, html { background-color: #f5f6fa !important; font-family: 'Segoe UI', sans-serif; color: #222 !important; }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #ffffff, #f0f0f0);
            min-height: 100vh;
            padding-top: 2rem;
        }
        .block-container {
            max-width: 900px;
            margin: auto;
            background: white;
            border-radius: 18px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            padding: 2rem;
        }
        h1, h2, h3 { color: #444 !important; }
        </style>
    """,
    "💼 Professional Blue": """
        <style>
        body, html { background-color: #e8f0fe !important; font-family: 'Roboto', sans-serif; color: #111 !important; }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #dfe9f3, #f3f8fe);
            min-height: 100vh;
            padding-top: 2rem;
        }
        .block-container {
            max-width: 900px;
            margin: auto;
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
            padding: 2rem;
        }
        h1, h2, h3 { color: #1a73e8 !important; }
        </style>
    """
}

# ---------- Apply Selected Theme CSS
st.markdown(THEMES[theme], unsafe_allow_html=True)

# ---------- HEADER
st.title("📊 Datalicious")
st.subheader("AI-Powered Summaries & Visuals from Raw Data")

# ---------- Upload Section
uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if not uploaded_file:
    st.info("Upload a file to get started!")
else:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        st.header("👀 Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.header("🧠 Smart Summary")
        if st.button("Generate Summary"):
            with st.spinner("Asking GPT-4..."):
                summary = summarize_dataset(df.head(7))
                st.success("Done!")
                st.markdown(summary)

        st.header("📊 Chart Generator")
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox("Pick a numeric column:", numeric_columns)
            top_n = st.slider("Top N values:", 5, 20, 10)
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found.")

        st.header("💬 Ask Dataset Questions")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your Question:", placeholder="e.g. What are top 5 categories?")

        if user_input:
            with st.spinner("Thinking..."):
                reply = ask_dataset_question(df, user_input, mode)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))

        for role, msg in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"🧑 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Error: {e}")








