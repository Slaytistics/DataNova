import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# ======================
# STYLING CONFIGURATION
# ======================
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True
)

dark_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

[data-testid="stAppViewContainer"] {
    background: url("https://i.imgur.com/1JiHshs.jpeg") no-repeat center center fixed;
    background-size: cover;
}

body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(15, 15, 21, 0.85);
    z-index: -1;
}

.block-container {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    backdrop-filter: blur(16px);
    box-shadow: 0 0 20px 2px #444;
    padding: 2rem 3rem 3rem 3rem !important;
}

.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff !important;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.figma-container {
    margin-top: 2rem;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.figma-iframe {
    width: 100%;
    height: 600px;
    border: none;
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ======================
# APP TITLE
# ======================
st.markdown("""
<div style='text-align: center; margin-bottom: 3rem;'>
    <span style='font-size: 3rem; font-weight: 900; color: #ffffff !important; letter-spacing: 2px; margin-bottom: 0.5rem; display: block;'>DATALICIOUS</span>
    <span style='font-size: 1.2rem; color: #eee; letter-spacing: 3px; font-weight: 500;'>SLEEK. SMART. STREAMLINED.</span>
</div>
""", unsafe_allow_html=True)

# ======================
# FILE UPLOAD SECTION
# ======================
st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], label_visibility="collapsed")

if uploaded_file:
    try:
        # Data Processing
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # Data Preview
        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        # AI Summary
        st.markdown('<h2 class="section-header"><i class="fa fa-lightbulb-o"></i> Generate Summary</h2>', unsafe_allow_html=True)
        if st.button("Generate Summary", key="summary_btn"):
            with st.spinner("Analyzing your data..."):
                summary = summarize_dataset(df.head(7))
                st.markdown(summary)

        # Visualization
        st.markdown('<h2 class="section-header"><i class="fa fa-bar-chart"></i> Chart Generator</h2>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        
        if numeric_columns:
            col1, col2 = st.columns(2)
            with col1:
                selected_column = st.selectbox("Choose column:", numeric_columns)
            with col2:
                top_n = st.slider("Top N values:", 5, 20, 10)
            
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for visualization")

        # Q&A Chat
        st.markdown('<h2 class="section-header"><i class="fa fa-comments"></i> Ask About This Dataset</h2>', unsafe_allow_html=True)
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"], key="qa_mode")
        user_input = st.text_input("Your question:", placeholder="e.g. What trends do you see in this data?")
        
        if user_input:
            with st.spinner("Analyzing your question..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        # Display chat history
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)

        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# ======================
# FIGMA INTEGRATION
# ======================
st.markdown("---")
st.markdown('<h2 class="section-header"><i class="fa fa-paint-brush"></i> Design Preview</h2>', unsafe_allow_html=True)

figma_url = st.text_input(
    "Paste Figma file URL to embed:",
    placeholder="https://www.figma.com/file/...",
    key="figma_url_input"
)

if figma_url:
    try:
        # Extract file key from URL
        if "figma.com/file/" in figma_url:
            file_key = figma_url.split("figma.com/file/")[1].split("/")[0]
        else:
            file_key = figma_url.split("figma.com/")[1].split("/")[0]
        
        # Embed the Figma prototype
        st.markdown(f"""
        <div class="figma-container">
            <iframe 
                class="figma-iframe" 
                src="https://www.figma.com/embed?embed_host=streamlit&url=https://www.figma.com/file/{file_key}" 
                allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 10px; font-size: 0.9em; color: #aaa; text-align: center;">
            <i class="fa fa-lightbulb-o"></i> Use <code>Shift+Scroll</code> to navigate horizontally
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error("Please enter a valid Figma file URL")

# Initial state message
if not uploaded_file and not figma_url:
    st.info("👈 Upload a CSV file or paste a Figma URL to begin")
