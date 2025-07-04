import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Custom Styles ---
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
        padding: 0rem 2rem 1.5rem 2rem !important;
        max-width: 800px;
        margin: auto;
    }

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f0f0f0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Dropdown and selectbox fixes */
    [data-baseweb="select"] {
        background-color: #fff !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.2) !important;
        color: #000 !important;
    }

    [data-baseweb="select"] * {
        color: #000 !important;
    }

    [data-baseweb="select"] input {
        color: #000 !important;
        background-color: transparent !important;
        pointer-events: none;
        caret-color: transparent;
    }

    [role="option"] {
        color: #000 !important;
        background-color: #fff !important;
    }

    [role="option"][aria-selected="true"] {
        background-color: #eee !important;
    }

    div[data-baseweb="popover"] {
        background-color: #fff !important;
        color: #000 !important;
        border: 1px solid #ccc !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown(
    """
    <div style="width: 100%; text-align: center; margin: 2rem 0 1rem 0;">
        <h1 style="font-size: 4rem; font-weight: 800; color: white; margin-bottom: 0.5rem;">DATALICIOUS</h1>
        <p style="font-size: 1.2rem; letter-spacing: 2px; color: white;">SLEEK. SMART. STREAMLINED.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma")
st.header("Upload Your Dataset")

# --- File Upload ---
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

        # --- Summary Section ---
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

        # --- Chart Generator ---
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

        # --- QnA Section ---
        st.header("Ask About This Dataset")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"], key="style_select")
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








