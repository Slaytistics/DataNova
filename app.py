import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🌄 Add background image and custom fonts + styles
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&family=Roboto+Slab&display=swap');

    [data-testid="stAppViewContainer"] {
        background-image: url("https://i.imgur.com/qo8IZvH.jpeg");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Poppins', sans-serif;
    }

    .block-container {
        padding: 2rem 3rem;
        max-width: 900px;
        margin: auto;
        background: transparent !important;
    }

    /* Remove background boxes */
    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .stDataFrame,
    .element-container,
    .stPlotlyChart,
    .chat-message,
    details {
        background-color: transparent !important;
        color: #222 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 12px;
    }

    input, textarea, select {
        background-color: rgba(255,255,255,0.85) !important;
        color: #222 !important;
        border: 1px solid #bbb !important;
        border-radius: 6px;
        font-family: 'Poppins', sans-serif;
    }

    [data-testid="stFileUploader"] > div {
        background-color: rgba(255,255,255,0.85) !important;
        border-radius: 6px;
    }

    button {
        background-color: rgba(240,240,240,0.9) !important;
        color: #222 !important;
        border: 1px solid #bbb !important;
        font-family: 'Poppins', sans-serif;
        border-radius: 6px;
    }

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #222 !important;
    }

    .stSlider > div > div > div > div {
        background-color: #666 !important;
    }

    .stDataFrame div {
        color: #222 !important;
    }

    /* Titles and headings with different colors and fonts */
    .css-1d391kg h1, .css-1d391kg .stTitle {
        color: #1B4F72;  /* Deep Blue */
        font-family: 'Roboto Slab', serif;
        font-weight: 700;
    }

    .css-1d391kg h2, .css-1d391kg .stHeader {
        color: #117A65; /* Teal */
        font-family: 'Roboto Slab', serif;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* Box around Generate Summary */
    .summary-box {
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid #117A65;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 📐 App layout and style
st.set_page_config(page_title="Datalicious", layout="wide")
st.title("Datalicious — AI Data Assistant")
st.markdown(
    "Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma"
)

st.divider()
st.header("Upload Your Dataset")

# 🔼 File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        # 🧼 Read and clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 👀 Dataset preview
        st.subheader("Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("Generate Summary")

        # 🧠 AI summary inside box
        summary = None
        with st.container():
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Generate Summary"):
                    with st.spinner("Calling Together AI..."):
                        summary = summarize_dataset(df.head(7))
                        st.success("Summary Generated!")
            with col2:
                st.markdown(
                    "The summary provides a GPT-style overview based on sample data."
                )
            if summary:
                st.markdown(f"#### Summary Output:\n{summary}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
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

        st.divider()
        st.header("Export to Figma")

        if summary:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(summary, dataset_name=dataset_name)
                    st.toast("Exported to Figma!")
                    st.success(result)

        st.divider()
        st.header("Ask About This Dataset")

        # 🧠 Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        # 🗨️ Styled chat display without emojis
        for role, msg in st.session_state.chat_history:
            bg = "#DFF2E1" if role == "user" else "#F0F0F0"
            prefix = "You:" if role == "user" else "AI:"
            st.markdown(
                f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px'><strong>{prefix}</strong><br>{msg}</div>",
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")
