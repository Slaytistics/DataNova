import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Enhanced Dark Theme & UI CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

/* Background image with overlay */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=1080");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
    font-family: 'Inter', sans-serif;
    position: relative;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    z-index: -1;
}

/* Main container styling */
.block-container {
    padding: 2rem 2rem 1.5rem 2rem !important;
    max-width: 800px;
    margin: auto;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    border-radius: 16px;
    background-color: rgba(20, 20, 20, 0.85);
}

/* Typography */
html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #f0f0f0 !important;
    font-family: 'Inter', sans-serif;
    text-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* Accent color for buttons */
.stButton > button {
    background-color: #1abc9c !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1.1rem;
    padding: 0.6rem 1.5rem;
    margin-bottom: 0.8rem !important;
    transition: background-color 0.3s, transform 0.2s;
    box-shadow: 0 2px 8px rgba(26,188,156,0.15);
}
.stButton > button:hover {
    background-color: #16a085 !important;
    transform: scale(1.04);
}

/* Input focus and selectbox */
.stTextInput > div > input:focus,
.stSelectbox > div > div:focus {
    border-color: #1abc9c !important;
    box-shadow: 0 0 8px #1abc9c !important;
}
[data-baseweb="select"] {
    background-color: rgba(30, 30, 30, 0.95) !important;
    color: #f0f0f0 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    transition: all 0.3s ease;
    padding: 8px !important;
}
[data-baseweb="select"]:hover {
    border: 1.5px solid #1abc9c !important;
}
[data-baseweb="select"] div,
[data-baseweb="select"] span {
    color: #f0f0f0 !important;
}
[data-baseweb="select"] svg {
    filter: brightness(200%) invert(100%) !important;
}
div[data-baseweb="menu"] {
    background-color: rgba(20, 20, 20, 0.95) !important;
    color: #f0f0f0 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
}
div[data-baseweb="menu"] div[role="option"] {
    background-color: transparent !important;
    color: #f0f0f0 !important;
    padding: 10px 14px !important;
}
div[data-baseweb="menu"] div[role="option"]:hover {
    background-color: rgba(26,188,156,0.15) !important;
}

/* DataFrame and Plotly chart backgrounds */
.stDataFrame table {
    background-color: rgba(15,15,15,0.6) !important;
    color: #f0f0f0 !important;
}
.js-plotly-plot .plotly {
    background-color: rgba(15,15,15,0.6) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Chat bubbles */
.chat-user {
    background-color: #1abc9c;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 8px;
    max-width: 80%;
    color: white;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(26,188,156,0.15);
    margin-left: auto;
}
.chat-ai {
    background-color: #34495e;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 8px;
    max-width: 80%;
    color: white;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(52,73,94,0.15);
    margin-right: auto;
}

/* Chat window scroll */
#chat-window {
    max-height: 320px;
    overflow-y: auto;
    margin-bottom: 1rem;
    padding-right: 8px;
}

/* Section headers with icons */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: #1abc9c;
    letter-spacing: 1px;
}
.section-header i {
    font-size: 1.5rem;
    color: #1abc9c;
}

/* Subtle section separation */
hr {
    border: none;
    border-top: 1.5px solid rgba(255,255,255,0.08);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# --- Title Section with Animation ---
st.markdown("""
<div style="width: 100%; text-align: center; margin: 2rem 0 1rem 0;">
    <h1 style="font-size: 4rem; font-weight: 800; color: white; margin-bottom: 0.5rem; letter-spacing: 2px; text-shadow: 0 4px 24px #1abc9c66;">
        <span style="animation: fadeIn 1.2s;">DATALICIOUS</span>
    </h1>
    <p style="font-size: 1.2rem; letter-spacing: 2px; color: #1abc9c; font-weight: 600; margin-bottom: 0;">
        SLEEK. SMART. STREAMLINED.
    </p>
</div>
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-30px);}
    to { opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# --- App Description & Upload ---
st.markdown(
    '<div style="font-size:1.1rem; color:#f0f0f0; margin-bottom:1.5rem;">'
    '<i class="fa fa-upload" style="color:#1abc9c; margin-right:8px;"></i>'
    'Upload structured data, generate insights, visualize trends, and export them professionally. '
    '<span style="color:#1abc9c;">Powered by Together AI + Figma</span>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown('<div class="section-header"><i class="fa fa-file-upload"></i>Upload Your Dataset</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # Preview
        st.markdown('<div class="section-header"><i class="fa fa-table"></i>Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        # Summary
        st.markdown('<div class="section-header"><i class="fa fa-lightbulb"></i>Generate Summary</div>', unsafe_allow_html=True)
        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated! 🎉")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")

        if summary:
            st.markdown(f"#### Summary Output:\n{summary}")

        # Chart Generator
        st.markdown('<div class="section-header"><i class="fa fa-chart-bar"></i>Chart Generator</div>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()

        if numeric_columns:
            with st.expander("Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        # Ask Dataset
        st.markdown('<div class="section-header"><i class="fa fa-comments"></i>Ask About This Dataset</div>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

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

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")

