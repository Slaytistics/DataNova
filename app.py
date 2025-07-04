import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# Custom styles with Inter font, dark theme, and background image
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=1080");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding: 1.5rem 2rem;
        max-width: 800px;
        margin: auto;
    }

    .stMarkdown, .stText, .stHeading, .stSubheader, .stCaption, .stCodeBlock {
        background-color: rgba(20, 20, 20, 0.55);
        padding: 10px 16px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 0.8rem;
        backdrop-filter: blur(3px);
    }

    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .element-container,
    .stPlotlyChart,
    .chat-message,
    details {
        background-color: rgba(15, 15, 15, 0.6) !important;
        color: #f0f0f0 !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 10px !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(4px);
        font-family: 'Inter', sans-serif;
    }

    input, textarea, select {
        background-color: rgba(30, 30, 30, 0.95) !important;
        color: #f0f0f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 6px;
        padding: 6px !important;
    }

    [data-baseweb="select"] {
        background-color: rgba(35, 35, 35, 0.95) !important;
        color: #f0f0f0 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    [data-baseweb="select"] * {
        color: #f0f0f0 !important;
    }

    [data-testid="stFileUploader"] > div {
        background-color: rgba(30, 30, 30, 0.9) !important;
        border-radius: 6px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    button {
        background-color: rgba(60, 60, 60, 0.9) !important;
        color: #f0f0f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: background-color 0.3s ease;
    }

    button:hover {
        background-color: rgba(80, 80, 80, 1) !important;
    }

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f0f0f0 !important;
        font-family: 'Inter', sans-serif;
    }

    .element-container {
        margin-bottom: 0.6rem !important;
    }

    .js-plotly-plot .plotly {
        background-color: rgba(15,15,15,0.85) !important;
    }

    .stDataFrame {
        background-color: rgba(15,15,15,0.7) !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .stDataFrame table {
        background-color: rgba(15,15,15,0.8) !important;
        color: #f0f0f0 !important;
    }

    .stSlider > div > div > div > div {
        background-color: #cccccc33 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Page setup
st.set_page_config(page_title="Datalicious", layout="wide")
st.markdown(
    """
    <div style="width: 100%; text-align: center; margin-bottom: 2rem;">
        <img src="https://drive.google.com/file/d/1t1LN6dcrCUzo6k51xyhO0fFHBDuRnxto/view?usp=sharing" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 0;" />
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma"
)
st.header("Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.header("Generate Summary")

        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated!")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")

        if summary:
            st.markdown(f"#### Summary Output:\n{summary}")

        st.header("Chart Generator")

        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)

                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        st.header("Ask About This Dataset")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")



