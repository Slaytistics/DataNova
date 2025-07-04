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

dark_css = """
<style>
/* General app styles */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Poppins', sans-serif !important;
    color: #fff;
}

/* App background image */
[data-testid="stAppViewContainer"] {
    background: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg") no-repeat center center fixed;
    background-size: cover;
    min-height: 100vh;
    padding-top: 6rem;
}

body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(15, 15, 21, 0.85);
    z-index: -1;
}

/* Container styling */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    backdrop-filter: blur(16px);
    box-shadow: 0 0 20px 2px #444;
    padding: 2rem 3rem 3rem 3rem !important;
}

/* Title block */
.title-block {
    text-align: center;
    margin-bottom: 3rem;
}
.title-block h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #ff69b4;
    letter-spacing: 2px;
}
.title-block p {
    font-size: 1.2rem;
    color: #eee;
    letter-spacing: 3px;
}

/* Buttons */
.stButton > button {
    background: #111 !important;
    color: white !important;
    font-weight: 700;
    border-radius: 30px;
    padding: 0.7rem 2.5rem;
    font-size: 1.1rem;
    box-shadow: 0 0 8px #222;
    transition: all 0.3s ease;
    border: none !important;
}
.stButton > button:hover {
    box-shadow: 0 0 12px #444;
    transform: scale(1.05);
}

/* SECTION HEADERS */
.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #ff69b4;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

/* Slider label text */
[data-testid="stSlider"] label {
    color: #000 !important;
    font-weight: 600;
}

/* Selectbox and text input fields */
div[data-baseweb="select"] > div,
input[type="text"],
textarea {
    background-color: #fff !important;
    color: #000 !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}

/* Dropdown options */
[data-testid="stSelectbox"] div[role="listbox"] > div {
    background-color: #fff !important;
    color: #000 !important;
}

/* Dropdown single value */
div[data-baseweb="select"] span {
    color: #000 !important;
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
    background: linear-gradient(135deg, #ff69b4, #9b30ff);
    color: #fff;
    border-radius: 24px 24px 24px 0;
    padding: 14px 20px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 16px rgba(255, 105, 180, 0.5);
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
st.markdown(dark_css, unsafe_allow_html=True)

# --- Main Title ---
st.markdown("""
<div class="title-block">
    <h1>DATALICIOUS</h1>
    <p>SLEEK. SMART. STREAMLINED.</p>
</div>
""", unsafe_allow_html=True)

# --- File Upload ---
st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        st.markdown('<h2 class="section-header"><i class="fa fa-lightbulb-o"></i> Generate Summary</h2>', unsafe_allow_html=True)
        if st.button("Generate Summary"):
            with st.spinner("Calling Together AI..."):
                summary = summarize_dataset(df.head(7))
                st.success("Summary Generated!")
                st.markdown(summary)

        st.markdown('<h2 class="section-header"><i class="fa fa-bar-chart"></i> Chart Generator</h2>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox("Choose column:", numeric_columns, label_visibility="visible", disabled=False)
            top_n = st.slider("Top N values:", 5, 20, 10)
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        st.markdown('<h2 class="section-header"><i class="fa fa-comments"></i> Ask About This Dataset</h2>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"], label_visibility="visible", disabled=False)
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
