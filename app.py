import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# ---------- Theme State Setup ----------
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "🔮 Neon Night"

# ---------- Sidebar Theme Selector ----------
st.sidebar.title("🎨 Theme Selector")
theme_options = ["🔮 Neon Night", "🧊 Cool Light", "💼 Professional Blue"]
selected = st.sidebar.selectbox("Choose UI Theme:", theme_options, index=theme_options.index(st.session_state.selected_theme))

# ---------- Detect and Apply Change ----------
if selected != st.session_state.selected_theme:
    st.session_state.selected_theme = selected
    st.experimental_rerun()

# ---------- CSS Themes ----------
THEMES = {
    "🔮 Neon Night": """
    <style>
    html, body { background-color: #0f0f15 !important; color: white !important; font-family: 'Poppins', sans-serif; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
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
    html, body { background-color: #f5f6fa !important; color: #222 !important; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom right, #ffffff, #e6f0f8);
    }
    .block-container {
        max-width: 900px;
        margin: auto;
        background: white;
        border-radius: 16px;
        box-shadow: 0 0 12px rgba(0,0,0,0.1);
        padding: 2rem;
    }
    h1, h2, h3 { color: #444 !important; }
    </style>
    """,
    "💼 Professional Blue": """
    <style>
    html, body { background-color: #e8f0fe !important; color: #222 !important; font-family: 'Roboto', sans-serif; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom right, #cfd9e8, #f3f8fe);
    }
    .block-container {
        max-width: 900px;
        margin: auto;
        background: #ffffff;
        border-radius: 14px;
        box-shadow: 0 0 12px rgba(0,0,0,0.08);
        padding: 2rem;
    }
    h1, h2, h3 { color: #1a73e8 !important; }
    </style>
    """
}

# ---------- Apply Selected Theme CSS ----------
st.markdown(THEMES[st.session_state.selected_theme], unsafe_allow_html=True)

# ---------- App Header ----------
st.title("📊 Datalicious")
st.subheader("AI-Powered Summaries & Visuals from Raw Data")

# ---------- Upload CSV ----------
uploaded_file = st.file_uploader("📥 Upload your dataset (.csv)", type=["csv"])

if not uploaded_file:
    st.info("Upload a dataset to begin exploring!")
else:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        # ---------- Data Preview ----------
        st.header("👀 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # ---------- GPT Summary ----------
        st.header("🧠 Smart Summary")
        if st.button("Generate Summary"):
            with st.spinner("Thinking like GPT-4..."):
                summary = summarize_dataset(df.head(7))
                st.success("Summary Ready!")
                st.markdown(f"📄 {summary}")

        # ---------- Chart Generator ----------
        st.header("📈 Chart Generator")
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox("Choose a numeric column:", numeric_columns)
            top_n = st.slider("Top N values:", 5, 20, 10)
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for chart generation.")

        # ---------- Q&A Section ----------
        st.header("💬 Ask a Question About This Dataset")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Ask something like: What’s the most common value?")

        if user_input:
            with st.spinner("Analyzing..."):
                reply = ask_dataset_question(df, user_input, mode)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))

        # Display chat history
        for role, msg in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"🧑 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

        # Clear chat button
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")









