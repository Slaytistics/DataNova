import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# Custom styles with Arial Italic font, colored headings, styled button, background image

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    [data-testid="stAppViewContainer"] {
        background: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=1080") center/cover fixed;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding: 1.2rem 1.5rem !important;
        max-width: 800px;
        margin: auto;
    }

    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .stDataFrame,
    .stPlotlyChart,
    .chat-message,
    details {
        background-color: rgba(15,15,15,0.85) !important;
        color: #e0e0e0 !important;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px !important;
        margin-bottom: 0.5rem !important;
        backdrop-filter: blur(4px);
    }

    input, textarea, select {
        background-color: rgba(30,30,30,0.95) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 4px;
        padding: 6px !important;
        margin: 0 !important;
    }

    button {
        background-color: rgba(60,60,60,0.9) !important;
        color: #f2f2f2 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 6px 12px !important;
        margin: 0 !important;
        transition: background-color 0.3s ease;
    }

    button:hover {
        background-color: rgba(80,80,80,0.95) !important;
    }

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
        margin: 0 !important;
        padding: 0 !important;
    }

    .element-container {
        margin-bottom: 0.5rem !important;
    }

    .stSlider > div > div > div > div {
        background-color: #cccccc33 !important;
    }

    .chat-user, .chat-ai {
        background: rgba(35,35,35,0.85);
        padding: 8px !important;
        border-radius: 6px;
        margin: 4px 0 !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255,255,255,0.08);
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
        <img src="https://i.imgur.com/4Hqe6a0.png" style="width: 100%; max-height: 250px; object-fit: cover; border-radius: 0;" />
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


