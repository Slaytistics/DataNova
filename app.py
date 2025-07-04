import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Replace with your actual imports
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# ------------------ Page Setup ------------------
st.set_page_config(page_title="Datalicious", layout="wide", initial_sidebar_state="expanded")

# ------------------ Session Setup ------------------
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "🔮 Neon Night"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""

# ------------------ Sidebar: Theme ------------------
st.sidebar.title("🎨 Theme & Navigation")
theme_options = ["🔮 Neon Night", "🧊 Cool Light", "💼 Professional Blue"]
selected = st.sidebar.selectbox("Select Theme", theme_options, index=theme_options.index(st.session_state.selected_theme))
if selected != st.session_state.selected_theme:
    st.session_state.selected_theme = selected
    st.experimental_rerun()

# ------------------ Sidebar: Sample Data ------------------
with st.sidebar.expander("📂 Load Sample Dataset"):
    if st.button("Load Titanic Dataset"):
        df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
        st.session_state.df = df
        st.success("Sample Titanic dataset loaded.")
        st.experimental_rerun()

# ------------------ THEME CSS ------------------
THEMES = {
    "🔮 Neon Night": """
        <style>
        html, body { background-color: #0f0f15; color: white; font-family: 'Poppins', sans-serif; }
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
        h1, h2, h3 { color: #ff69b4; }
        </style>
    """,
    "🧊 Cool Light": """
        <style>
        html, body { background-color: #f5f6fa; color: #222; font-family: 'Segoe UI', sans-serif; }
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
        h1, h2, h3 { color: #333; }
        </style>
    """,
    "💼 Professional Blue": """
        <style>
        html, body { background-color: #e8f0fe; color: #222; font-family: 'Roboto', sans-serif; }
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
        h1, h2, h3 { color: #1a73e8; }
        </style>
    """
}
st.markdown(THEMES[st.session_state.selected_theme], unsafe_allow_html=True)

# ------------------ Title ------------------
st.title("📊 Datalicious")
st.caption("AI-generated summaries, visualizations, and answers from your dataset.")

# ------------------ File Upload ------------------
uploaded_file = st.file_uploader("📥 Upload your dataset (.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
elif "df" not in st.session_state:
    st.info("Upload a file or load a sample dataset to begin.")
    st.stop()
else:
    df = st.session_state.df

# ------------------ Data Preview ------------------
st.header("👁 Preview Your Data")
st.dataframe(df.head(), use_container_width=True)

# ------------------ Data Info ------------------
with st.expander("📊 Quick Stats"):
    st.write(f"**Rows:** {df.shape[0]}, **Columns:** {df.shape[1]}")
    st.write("**Missing Values (%):**")
    st.write((df.isnull().sum() / len(df) * 100).round(2).astype(str) + "%")
    st.write("**Data Types:**")
    st.write(df.dtypes)

# ------------------ Summary Section ------------------
st.header("🧠 AI Summary")
if st.button("Generate Summary"):
    with st.spinner("Calling GPT..."):
        st.session_state.summary_text = summarize_dataset(df.head(7))
        st.success("Done!")
if st.session_state.summary_text:
    st.text_area("📄 Summary Output", st.session_state.summary_text, height=200)
    summary_buffer = io.StringIO(st.session_state.summary_text)
    st.download_button("📤 Download Summary", data=summary_buffer, file_name="summary.txt", mime="text/plain")

# ------------------ Chart Generator ------------------
st.header("📈 Chart Generator")
num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
if num_cols:
    col = st.selectbox("Choose numeric column to visualize", num_cols)
    top_n = st.slider("Top N values to show", 5, 20, 10)
    fig = plot_top_column(df, col, top_n)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No numeric columns to plot.")

# ------------------ Q&A Chat Section ------------------
st.header("💬 Ask Your Dataset")
mode = st.selectbox("Response Style", ["Normal", "Explain like I'm 5", "Detailed"])
user_q = st.text_input("Type a question (e.g., Which column has highest value?)")
if user_q:
    with st.spinner("AI is thinking..."):
        reply = ask_dataset_question(df, user_q, mode)
        st.session_state.chat_history.append(("You", user_q))
        st.session_state.chat_history.append(("AI", reply))

# Chat Display
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}**: {msg}")

# Clear Chat
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()










