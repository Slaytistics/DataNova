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
/* ... your existing CSS remains unchanged above ... */

/* Input fields and dropdowns (font color updated) */
.stTextInput > div > input,
.stSelectbox > div > div,
.css-1wa3eu0-placeholder {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: #00ffff !important;  /* ✅ NEON CYAN TEXT COLOR */
    font-weight: 600;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
}

/* File uploader label font color */
[data-testid="stFileUploader"] label {
    color: #00ffff !important;
    font-weight: 600;
}

/* Dropdown menu text */
.css-3vnyiq-option {
    background-color: #222 !important;
    color: #00ffff !important;
    font-weight: 500;
    font-size: 1rem;
}
.css-3vnyiq-option:hover {
    background-color: #444 !important;
    color: #00ffff !important;
}

/* Optional: dropdown selected value styling */
.css-1dimb5e-singleValue {
    color: #00ffff !important;
    font-weight: 600;
}

/* ... rest of your CSS continues below ... */
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
