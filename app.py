import streamlit as st
import pandas as pd
import plotly.express as px

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Google Fonts and Material Icons ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Nunito:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)

# --- Custom CSS for Modern Pastel UI ---
st.markdown("""
<style>
body, html, div, span, label {
    font-family: 'Montserrat', 'Nunito', sans-serif !important;
    color: #222 !important;
    background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%) !important;
    margin: 0; padding: 0;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%) !important;
    min-height: 100vh;
    padding-left: 220px !important;
}
#side-nav {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 200px;
    background: rgba(255,255,255,0.85);
    box-shadow: 2px 0 24px 0 rgba(60,60,120,0.08);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 2.5rem;
    z-index: 100;
}
#side-nav .nav-item {
    width: 100%;
    padding: 1.2rem 0;
    text-align: center;
    font-size: 1.1rem;
    color: #6366f1;
    cursor: pointer;
    border-left: 4px solid transparent;
    transition: background 0.2s, border-color 0.2s;
}
#side-nav .nav-item.selected, #side-nav .nav-item:hover {
    background: #eef2ff;
    border-left: 4px solid #6366f1;
    color: #3730a3;
}
#side-nav .material-icons {
    font-size: 2rem;
    margin-bottom: 0.2rem;
    display: block;
}
.card {
    background: rgba(255,255,255,0.85);
    border-radius: 20px;
    box-shadow: 0 8px 32px 0 rgba(60,60,120,0.10);
    padding: 2.5rem 2rem 2rem 2rem;
    margin-bottom: 2.5rem;
    animation: fadeIn 0.7s;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(30px);}
    to { opacity: 1; transform: translateY(0);}
}
.section-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #6366f1;
    margin-bottom: 1.2rem;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.stButton > button {
    background: linear-gradient(90deg, #a5b4fc, #fbc2eb);
    color: #3730a3 !important;
    font-weight: 700;
    border-radius: 12px;
    padding: 0.7rem 2rem;
    border: none !important;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px #e0e7ff;
    transition: background 0.2s, transform 0.1s;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #6366f1, #fbc2eb);
    color: #fff !important;
    transform: scale(1.04);
}
.stDataFrame table {
    background: rgba(248,250,252,0.7) !important;
    color: #222 !important;
    border-radius: 12px;
    box-shadow: 0 2px 8px #e0e7ff;
}
.js-plotly-plot .plotly {
    background: rgba(248,250,252,0.7) !important;
    border-radius: 12px;
    box-shadow: 0 2px 8px #e0e7ff;
}
.chat-bubble-user {
    background: linear-gradient(90deg, #a5b4fc, #fbc2eb);
    color: #3730a3;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin-bottom: 8px;
    max-width: 80%;
    margin-left: auto;
    font-weight: 500;
}
.chat-bubble-ai {
    background: linear-gradient(90deg, #fbc2eb, #a5b4fc);
    color: #3730a3;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin-bottom: 8px;
    max-width: 80%;
    margin-right: auto;
    font-weight: 500;
}
#chat-window {
    max-height: 320px;
    overflow-y: auto;
    margin-bottom: 1rem;
    padding-right: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
nav_options = [
    ("Upload", "cloud_upload"),
    ("Preview", "table_chart"),
    ("Summary", "insights"),
    ("Charts", "bar_chart"),
    ("Q&A", "chat"),
]
if "nav" not in st.session_state:
    st.session_state.nav = "Upload"

def nav_click(label):
    st.session_state.nav = label

# Render sidebar
side_nav_html = '<div id="side-nav">'
for label, icon in nav_options:
    selected = "selected" if st.session_state.nav == label else ""
    side_nav_html += f'''
    <div class="nav-item {selected}" onclick="window.location.search='?nav={label}'">
        <span class="material-icons">{icon}</span>{label}
    </div>
    '''
side_nav_html += '</div>'
st.markdown(side_nav_html, unsafe_allow_html=True)

# Handle navigation via query param (simulate tab switch)
import urllib.parse
params = st.experimental_get_query_params()
if "nav" in params and params["nav"][0] in [x[0] for x in nav_options]:
    st.session_state.nav = params["nav"][0]
    st.experimental_set_query_params()  # clear params

# --- Main Content Area ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="fileuploader", label_visibility="collapsed")

if st.session_state.nav == "Upload":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span class="material-icons">cloud_upload</span>Upload Your Dataset</div>', unsafe_allow_html=True)
    if not uploaded_file:
        st.info("Upload a CSV file to begin your Datalicious journey.")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        if st.session_state.nav == "Preview":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="material-icons">table_chart</span>Preview</div>', unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.nav == "Summary":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="material-icons">insights</span>Generate Summary</div>', unsafe_allow_html=True)
            summary = None
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Generate Summary"):
                    with st.spinner("Calling Together AI..."):
                        summary = summarize_dataset(df.head(7))
                        st.success("Summary Generated! 🎉")
            with col2:
                st.markdown("The summary provides a GPT-style overview based on sample data.")
            if summary:
                st.markdown(f'<div style="background:#eef2ff;border-radius:12px;padding:1.2rem 1rem;margin-top:1rem;">{summary}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.nav == "Charts":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="material-icons">bar_chart</span>Chart Generator</div>', unsafe_allow_html=True)
            numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
            if numeric_columns:
                with st.expander("Chart Controls", expanded=True):
                    selected_column = st.selectbox("Choose column:", numeric_columns)
                    top_n = st.slider("Top N values:", 5, 20, 10)
                    fig = plot_top_column(df, selected_column, top_n=top_n)
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["sendDataToCloud"],
                        }
                    )
            else:
                st.warning("No numeric columns found for charts.")
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.nav == "Q&A":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"><span class="material-icons">chat</span>Ask About This Dataset</div>', unsafe_allow_html=True)
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
            user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

            if user_input:
                with st.spinner("Thinking like a data analyst..."):
                    reply = ask_dataset_question(df, user_input, mode=mode)
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("ai", reply))

            st.markdown('<div id="chat-window">', unsafe_allow_html=True)
            for role, msg in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"<div class='chat-bubble-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.experimental_rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")




