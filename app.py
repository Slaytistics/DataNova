import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os

# Import your corrected backend modules
from summarizer import summarize_dataset
from visualizer import plot_top_column  # Ensure this returns a plotly fig
from qna import ask_dataset_question

# --- Page Config ---
st.set_page_config(page_title="DataNova AI", page_icon="🚀", layout="wide")

# --- CSS Styling (Optimized) ---
dark_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .stCard {
        background: rgba(30, 41, 59, 0.7);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #f97316 !important; font-weight: 900 !important; }
    
    /* Custom Chat Styling */
    .chat-user { background: #1e293b; border-left: 5px solid #f97316; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    .chat-ai { background: #334155; border-left: 5px solid #38bdf8; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div style='text-align: center; padding: 40px 0;'>
    <h1 style='font-size: 4rem; margin-bottom: 0;'>DATANOVA <span style='color:white'>AI</span></h1>
    <p style='letter-spacing: 5px; color: #94a3b8;'>PREDICTIVE . DESIGN . ANALYTICS</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.title("Settings")
    analysis_style = st.selectbox("AI Summary Style", ["Executive Summary", "Technical Analysis", "Business Insights"])
    chat_mode = st.selectbox("Chat Depth", ["Normal", "Deep", "Quick"])
    if st.button("Clear Cache & History"):
        st.session_state.clear()
        st.rerun()

# --- Layout: Two Columns ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Step 1: Data Ingestion")
    uploaded_file = st.file_uploader("Drop your CSV here", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Cleaning logic from main.py
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        
        st.success(f"Loaded {uploaded_file.name} successfully!")
        st.dataframe(df.head(10), use_container_width=True)

        # --- AI Summarization ---
        st.markdown("### 🤖 Step 2: AI Narrative")
        if st.button(f"Generate {analysis_style}"):
            with st.spinner("Synthesizing data..."):
                summary = summarize_dataset(df, style=analysis_style)
                st.markdown(f"<div class='stCard'>{summary}</div>", unsafe_allow_html=True)

with col2:
    if uploaded_file:
        st.markdown("### 🎨 Step 3: Figma Key View")
        figma_key = st.text_input("Figma File Key", placeholder="Enter key...")
        
        if figma_key:
            st.markdown(f"""
            <iframe style="border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 12px;" 
            width="100%" height="300" 
            src="https://www.figma.com/embed?embed_host=share&url=https://www.figma.com/file/{figma_key}" 
            allowfullscreen></iframe>
            """, unsafe_allow_html=True)
            
        st.markdown("### 📊 Quick Visualization")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            viz_col = st.selectbox("Select Target", numeric_cols)
            # Use plotly for the interactive feel
            fig = px.histogram(df, x=viz_col, color_discrete_sequence=['#f97316'])
            st.plotly_chart(fig, use_container_width=True)

# --- Chat Interface (Full Width) ---
if uploaded_file:
    st.markdown("---")
    st.markdown("### 💬 DataNova Smart Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        role_class = "chat-user" if message["role"] == "user" else "chat-ai"
        st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Ask anything about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = ask_dataset_question(df, prompt, mode=chat_mode)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("Please upload a CSV file to unlock AI Analysis and Chat features.")