import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# Custom styles with Arial Italic font, colored headings, styled button, background image

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .block-container {{
        padding: 2rem 3rem;
        max-width: 900px;
        margin: auto;
    }}

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
    details {{
        background-color: rgba(15, 15, 15, 0.75) !important;
        color: white !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 12px;
    }}

    input, textarea, select {{
        background-color: rgba(40, 40, 40, 0.95) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 6px;
    }}

    [data-testid="stFileUploader"] > div {{
        background-color: rgba(30, 30, 30, 0.85) !important;
        border-radius: 6px;
    }}

    button {{
        background-color: rgba(50, 50, 50, 0.9) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }}

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: white !important;
    }}

    .stSlider > div > div > div > div {{
        background-color: #ffffff88 !important;
    }}

    .stDataFrame div {{
        color: white !important;
    }}

    .chat-user, .chat-ai {{
        background: rgba(40, 40, 40, 0.85);
        padding: 10px;
        border-radius: 8px;
        margin: 6px;
        color: white !important;
    }}
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
st.divider()
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

        st.divider()
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
