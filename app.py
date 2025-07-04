import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- FontAwesome for icons ---
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True,
)

# --- Custom Styling ---
soft_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

body, html, div, span, label {
    font-family: 'Poppins', sans-serif !important;
    color: #ffffff !important;
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

body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(20, 15, 10, 0.7);
    z-index: -1;
}

/* Container */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 18px;
    backdrop-filter: blur(14px);
    box-shadow: 0 0 15px rgba(50, 30, 10, 0.4);
    padding: 2rem 2.5rem 3rem 2.5rem !important;
}

/* Title */
.title-block {
    text-align: center;
    margin-bottom: 2.5rem;
}
.title-block h1 {
    font-size: 2.8rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.3rem;
}
.title-block p {
    font-size: 1.1rem;
    color: #dddddd;
    font-weight: 500;
    letter-spacing: 2px;
}

/* Section Header (no underline) */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 1.5rem 0 1rem 0;
}

/* Button */
.stButton > button {
    background: #2a1e14;
    color: #f5f5f5 !important;
    font-weight: 600;
    border-radius: 25px;
    padding: 0.6rem 2rem;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
    border: none !important;
    font-size: 1rem;
}
.stButton > button:hover {
    background: #3b2a1c;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    transform: scale(1.02);
}

/* Inputs & Dropdowns */
input, .stTextInput input, .stSelectbox div div {
    background-color: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #ffffff44 !important;
    padding: 0.6rem 1rem !important;
    font-size: 1rem !important;
}

/* Chat Bubbles */
.chat-user {
    background: #ffffff;
    color: #1d1d1d;
    border-radius: 20px 20px 0 20px;
    padding: 12px 18px;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
    font-weight: 600;
    margin-bottom: 10px;
}
.chat-ai {
    background: #2a1e14;
    color: #ffffff;
    border-radius: 20px 20px 20px 0;
    padding: 12px 18px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    font-weight: 600;
    margin-bottom: 10px;
}

#chat-window {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 1.5rem;
}
/* --- Fix dropdown options visibility --- */
/* --- Dark-themed button (no muddy brown) --- */
.stButton > button {
    background: rgba(255, 255, 255, 0.07);
    color: #ffffff !important;
    font-weight: 600;
    border-radius: 25px;
    padding: 0.6rem 2rem;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
.stButton > button:hover {
    background: rgba(255, 255, 255, 0.12);
    transform: scale(1.02);
}

/* --- SELECTBOX (Dropdown) VISIBILITY FIX --- */
div[data-baseweb="select"] {
    background-color: rgba(0, 0, 0, 0.5) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

/* Text inside the select control */
div[data-baseweb="select"] * {
    color: #ffffff !important;
    font-weight: 500 !important;
}

/* Dropdown menu background */
div[data-baseweb="menu"] {
    background-color: rgba(15, 15, 15, 0.95) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}

/* Options inside dropdown */
div[data-baseweb="menu"] div[role="option"] {
    background-color: transparent !important;
    color: #ffffff !important;
    padding: 10px 15px;
    font-weight: 500;
}

/* Hover effect */
div[data-baseweb="menu"] div[role="option"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
}

/* --- Slider value labels (e.g., 5 and 20) fix --- */
.css-1y4p8pa {
    color: #ffffff !important;
    font-weight: 500;
    font-size: 1rem;
}


</style>
"""
st.markdown(soft_css, unsafe_allow_html=True)

# --- Title Block ---
st.markdown("""
<div class="title-block">
    <h1>DATALICIOUS</h1>
    <p>SLEEK. SMART. STREAMLINED.</p>
</div>
""", unsafe_allow_html=True)

# --- Upload Dataset ---
st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # --- Preview Section ---
        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        # --- Summary Generator ---
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

        # --- Q&A Section ---
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
