import streamlit as st
import pandas as pd
import plotly.express as px

# Import your actual functions
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Wide layout setup
st.set_page_config(page_title="Datalicious", layout="wide")

# --- Session state for theme
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "🔮 Neon Night"

# --- Sidebar Theme Selector
st.sidebar.title("🎨 Theme")
theme_options = ["🔮 Neon Night", "🧊 Cool Light", "💼 Professional Blue"]
selected = st.sidebar.selectbox("Select Theme", theme_options, index=theme_options.index(st.session_state.selected_theme))
if selected != st.session_state.selected_theme:
    st.session_state.selected_theme = selected
    st.experimental_rerun()

# --- CSS Themes
THEMES = {
    "🔮 Neon Night": """
        <style>
        html, body {
            background-color: #0f0f15 !important;
            color: white !important;
            font-family: 'Poppins', sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 2rem;
        }
        .block-container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            box-shadow: 0 0 25px #ff69b4, 0 0 40px #9b30ff;
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #ff69b4 !important;
        }
        </style>
    """,
    "🧊 Cool Light": """
        <style>
        html, body {
            background-color: #f5f6fa !important;
            color: #222 !important;
            font-family: 'Segoe UI', sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #ffffff, #e6f0f8);
            padding: 2rem;
        }
        .block-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 0 12px rgba(0,0,0,0.08);
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #333 !important;
        }
        </style>
    """,
    "💼 Professional Blue": """
        <style>
        html, body {
            background-color: #e8f0fe !important;
            color: #222 !important;
            font-family: 'Roboto', sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #cfd9e8, #f3f8fe);
            padding: 2rem;
        }
        .block-container {
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 0 12px rgba(0,0,0,0.1);
            padding: 2rem;
        }
        h1, h2, h3 {
            color: #1a73e8 !important;
        }
        </style>
    """
}

# --- Inject selected CSS
st.markdown(THEMES[st.session_state.selected_theme], unsafe_allow_html=True)

# --- HEADER
st.title("📊 Datalicious")
st.subheader("Turn your raw data into summaries, charts, and answers — instantly!")

# --- FILE UPLOAD
uploaded_file = st.file_uploader("📥 Upload your dataset (.csv)", type=["csv"])

if not uploaded_file:
    st.info("Please upload a CSV file to get started.")
else:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        # --- DATA PREVIEW
        st.header("👀 Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        st.markdown(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")

        # --- SUMMARY SECTION
        st.header("🧠 AI Summary")
        if st.button("Generate Summary"):
            with st.spinner("Generating summary using GPT..."):
                summary = summarize_dataset(df.head(7))
                st.success("Summary Ready!")
                st.markdown(f"📄 {summary}")

        # --- CHART GENERATOR
        st.header("📈 Chart Generator")
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        if numeric_columns:
            col = st.selectbox("Choose numeric column", numeric_columns)
            top_n = st.slider("Top N values", 5, 20, 10)
            fig = plot_top_column(df, col, top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns available for charting.")

        # --- Q&A SECTION
        st.header("💬 Ask About Your Data")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Ask a question (e.g., What is the most common value?)")

        if user_input:
            with st.spinner("Thinking..."):
                answer = ask_dataset_question(df, user_input, mode)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", answer))

        for speaker, message in st.session_state.chat_history:
            if speaker == "You":
                st.markdown(f"🧑 **You:** {message}")
            else:
                st.markdown(f"🤖 **AI:** {message}")

        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")









