import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column

# Load API key
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# Page setup
st.set_page_config(page_title="📊 Datalicious — AI Data Summary", layout="centered")
st.markdown("""
    <style>
        /* Dropdown visibility fix */
        .stSelectbox > div {
            z-index: 9999 !important;
        }

        /* Card styling */
        .stButton > button {
            background-color: #111;
            color: white;
            padding: 0.75em 1.5em;
            border-radius: 10px;
            font-weight: bold;
        }

        /* Headings spacing */
        h2 {
            margin-top: 2em;
        }

        /* Increase z-index for dropdown containers */
        section.main > div {
            overflow: visible !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🌌 Datalicious — AI-Powered Insights from Your Dataset")

# Upload section
st.header("📁 Upload Your CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded and read successfully.")
    st.dataframe(df.head())

    # Summary Section
    st.header("🧠 Generate Summary")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Generate Summary"):
            summary = summarize_dataset(df, api_key=OPENROUTER_API_KEY)
            st.write("**AI Summary:**")
            st.write(summary)
    with col2:
        st.info("The summary provides a GPT-style overview based on sample data.")

    # Chart Section
    st.header("📊 Chart Generator")
    st.subheader("Chart Controls")

    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    if numeric_columns:
        selected_col = st.selectbox("Choose column:", numeric_columns)
        n_top = st.slider("Top N values:", min_value=5, max_value=20, value=10)

        if selected_col:
            fig = plot_top_column(df, selected_col, n=n_top)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No numeric columns available for charting.")

    # Chat with Dataset
    st.header("💬 Ask the AI")
    st.subheader("Chat with your data")

    style = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
    prompt = st.text_input("You:", placeholder="Ask anything about the dataset...")
    if prompt:
        from summarizer import chat_with_data
        reply = chat_with_data(df, prompt, style=style, api_key=OPENROUTER_API_KEY)
        st.markdown("**AI:**")
        st.write(reply)

else:
    st.info("Please upload a CSV file to begin.")
