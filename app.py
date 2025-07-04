import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- FontAwesome ---
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True,
)

# --- Dark CSS & UI Fixes ---
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

body, html, div, span, label {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF !important;
    background-color: transparent !important;
    margin: 0; padding: 0;
}

[data-testid="stAppViewContainer"] {
    background: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg") no-repeat center center fixed;
    background-size: cover;
    min-height: 100vh;
    padding-top: 6rem;
    position: relative;
}

/* Overlay */
body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(15, 15, 21, 0.85);
    z-index: -1;
}

/* Container */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    backdrop-filter: blur(16px);
    box-shadow: 0 0 20px 2px #2b2b2b, 0 0 30px 8px #111;
    padding: 2rem 3rem 3rem 3rem !important;
}

/* Title */
.title-block {
    text-align: center;
    margin-bottom: 3rem;
}
.title-block h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
}
.title-block p {
    font-size: 1.2rem;
    color: #ccc;
    letter-spacing: 3px;
    font-weight: 500;
}

/* Buttons */
.stButton > button {
    background: #111 !important;
    color: #ffffff !important;
    font-weight: 700;
    border-radius: 30px;
    padding: 0.7rem 2.5rem;
    border: none !important;
    font-size: 1.1rem;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #222 !important;
    transform: scale(1.03);
}

/* Headings */
.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
    position: relative;
}
.section-header::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -6px;
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #999, #ccc);
    border-radius: 4px;
}

/* Dropdown Fixes */
div[data-baseweb="select"] {
    width: 100% !important;
    max-width: 600px;
    background-color: rgba(0, 0, 0, 0.6) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
div[data-baseweb="select"] div[role="button"] {
    padding: 0.8rem 1rem !important;
    overflow: hidden;
    white-space: nowrap;
    color: #fff !important;
}
div[data-baseweb="select"] input {
    pointer-events: none !important;
    opacity: 0 !important;
    height: 0px !important;
}

/* Dropdown menu */
div[data-baseweb="menu"] {
    background-color: #111 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    box-shadow: 0 0 12px rgba(0,0,0,0.5);
    z-index: 99999 !important;
}
div[data-baseweb="menu"] div[role="option"] {
    padding: 12px 20px;
    font-size: 1rem;
    color: #fff !important;
    background: transparent !important;
    transition: background 0.2s ease;
}
div[data-baseweb="menu"] div[role="option"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    cursor: pointer;
}

/* Chat Bubbles */
.chat-user {
    background: linear-gradient(135deg, #00ffff, #32cd32);
    color: #000;
    border-radius: 24px 24px 0 24px;
    padding: 14px 20px;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(0, 255, 255, 0.5);
    font-weight: 600;
    margin-bottom: 12px;
}
.chat-ai {
    background: linear-gradient(135deg, #444, #666);
    color: #fff;
    border-radius: 24px 24px 24px 0;
    padding: 14px 20px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 16px rgba(255, 255, 255, 0.1);
    font-weight: 600;
    margin-bottom: 12px;
}
#chat-window {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 1.5rem;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<div class="title-block">
    <h1>DATALICIOUS</h1>
    <p>SLEEK. SMART. STREAMLINED.</p>
</div>
""", unsafe_allow_html=True)

# --- Upload ---
st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # --- Preview ---
        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        # --- Summary ---
        st.markdown('<h2 class="section-header"><i class="fa fa-lightbulb-o"></i> Generate Summary</h2>', unsafe_allow_html=True)
        if st.button("Generate Summary"):
            with st.spinner("Calling Together AI..."):
                summary = summarize_dataset(df.head(7))
                st.success("Summary Generated!")
                st.markdown(summary)

        # --- Chart Generator ---
        st.markdown('<h2 class="section-header"><i class="fa fa-bar-chart"></i> Chart Generator</h2>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox("Choose column:", numeric_columns)
            top_n = st.slider("Top N values:", 5, 20, 10)
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        # --- Q&A Chat ---
        st.markdown('<h2 class="section-header"><i class="fa fa-comments"></i> Ask About This Dataset</h2>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        st.markdown('<div id="chat-window">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")
