import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# 1. Theme selection in sidebar
st.sidebar.title("🎨 Theme Selector")
theme = st.sidebar.radio("Choose your theme:", ["🔮 Neon Night", "🧊 Cool Light", "💼 Professional Blue"])

# 2. Theme CSS definitions
NEON_CSS = """<style>body, html { background-color: #0f0f15 !important; font-family: 'Poppins', sans-serif; color: white !important; }
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
</style>"""

LIGHT_CSS = """<style>
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
</style>"""

PROFESSIONAL_CSS = """<style>
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
</style>"""

# 3. Apply selected theme
if theme == "🔮 Neon Night":
    st.markdown(NEON_CSS, unsafe_allow_html=True)
elif theme == "🧊 Cool Light":
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)
elif theme == "💼 Professional Blue":
    st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)

# --- Header ---
st.title("📊 Datalicious")
st.subheader("AI-Powered Summaries + Visuals = Magic on Datasets")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your dataset (.csv)", type=["csv"])

if not uploaded_file:
    st.info("🚀 Upload a CSV to explore smart infographics.")
else:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        st.header("🔍 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.header("🧠 Generate Summary")
        if st.button("Generate Summary"):
            with st.spinner("Thinking like GPT-4..."):
                summary = summarize_dataset(df.head(7))
                st.success("✨ Summary Ready!")
                st.markdown(f"📄 {summary}")

        st.header("📈 Chart Generator")
        numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
        if numeric_columns:
            col = st.selectbox("Select column to plot:", numeric_columns)
            top_n = st.slider("Top N Values", 5, 20, 10)
            fig = plot_top_column(df, col, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns available.")

        st.header("💬 Ask a Question")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer Style", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Type your question here...")

        if user_input:
            with st.spinner("Analyzing..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))

        for sender, msg in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"🧑 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"Error: {e}")







