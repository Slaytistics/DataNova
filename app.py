import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Custom Dark Theme Styling ---
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

    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .element-container,
    .stPlotlyChart,
    .chat-message,
    details {
        background-color: rgba(15, 15, 15, 0.3) !important;
        color: #f0f0f0 !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 10px !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(2px);
    }

    .stDataFrame table {
        background-color: rgba(15,15,15,0.6) !important;
        color: #f0f0f0 !important;
    }

    .js-plotly-plot .plotly {
        background-color: rgba(15,15,15,0.6) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    """
    <div style="width: 100%; text-align: center; margin: 2rem 0 1rem 0;">
        <h1 style="font-size: 4rem; font-weight: 800; color: white; margin-bottom: 0.5rem;">DATALICIOUS</h1>
        <p style="font-size: 1.2rem; letter-spacing: 2px; color: white;">SLEEK. SMART. STREAMLINED.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma")
st.header("Upload Your Dataset")

# --- Upload ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # --- Preview ---
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
                st.markdown("#### Choose column:")

                # Custom HTML Dropdown with black text & white background
                html_dropdown = f"""
                <script>
                function updateDropdown(value) {{
                    const input = window.parent.document.querySelector('input[name="custom_dropdown_column"]');
                    if (input) {{
                        input.value = value;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}
                </script>

                <select onchange="updateDropdown(this.value)" style="
                    width: 100%;
                    padding: 12px;
                    font-size: 16px;
                    background-color: white;
                    color: black;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    margin-bottom: 10px;
                ">
                    <option disabled selected>Select a column</option>
                    {''.join(f'<option value="{col}">{col}</option>' for col in numeric_columns)}
                </select>
                """

                components.html(html_dropdown, height=100)
                selected_column = st.text_input("Selected Column", key="custom_dropdown_column", label_visibility="collapsed")

                if selected_column:
                    top_n = st.slider("Top N values:", 5, 20, 10)
                    fig = plot_top_column(df, selected_column, top_n=top_n)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        # --- Q&A Section ---
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











