import streamlit as st
import pandas as pd
import plotly.express as px
import requests

BACKEND_URL = "https://your-render-backend-url/api"  # 🔴 change this

st.set_page_config(page_title="DataNova AI", page_icon="🚀", layout="wide")

# ---------------- CSS ---------------- #
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    color: #f8fafc;
}
.stCard {
    background: rgba(30, 41, 59, 0.7);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.chat-user { background: #1e293b; padding: 10px; border-radius: 8px; }
.chat-ai { background: #334155; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#f97316'>DATANOVA AI</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

analysis_style = st.selectbox("AI Summary Style", ["Executive Summary","Technical Analysis","Business Insights"])
chat_mode = st.selectbox("Chat Mode", ["Normal","Deep","Quick"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())

    # -------- SUMMARY -------- #
    if st.button("Generate Summary"):
        with st.spinner("Analyzing..."):
            files = {"file": uploaded_file}
            data = {"style": analysis_style}

            res = requests.post(f"{BACKEND_URL}/summary", files=files, data=data)

            if res.status_code == 200:
                summary = res.json()["summary"]
                st.markdown(f"<div class='stCard'>{summary}</div>", unsafe_allow_html=True)
            else:
                st.error("Summary failed")

    # -------- VISUALIZATION -------- #
    st.markdown("### Visualization")

    chart_type = st.selectbox("Chart Type", ["bar","line","scatter","hist"])
    x_axis = st.selectbox("X Axis", df.columns)
    y_axis = st.selectbox("Y Axis", df.columns)
    limit = st.slider("Number of rows", 10, 100, 50)

    if st.button("Generate Chart"):
        with st.spinner("Generating chart..."):
            files = {"file": uploaded_file}
            data = {
                "chart_type": chart_type,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "limit": limit
            }

            res = requests.post(f"{BACKEND_URL}/visualize", files=files, data=data)

            if res.status_code == 200:
                img = res.json()["chart"]
                st.image(f"data:image/png;base64,{img}")
            else:
                st.error("Visualization failed")

    # -------- CHATBOT -------- #
    st.markdown("### 💬 DataNova Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        css = "chat-user" if msg["role"]=="user" else "chat-ai"
        st.markdown(f"<div class='{css}'>{msg['content']}</div>", unsafe_allow_html=True)

    question = st.chat_input("Ask about your dataset...")

    if question:
        st.session_state.messages.append({"role":"user","content":question})

        files = {"file": uploaded_file}
        data = {"question": question, "mode": chat_mode}

        with st.spinner("Thinking..."):
            res = requests.post(f"{BACKEND_URL}/chat", files=files, data=data)

            if res.status_code == 200:
                answer = res.json()["answer"]
            else:
                answer = "Error contacting AI service."

        st.session_state.messages.append({"role":"assistant","content":answer})
        st.rerun()

else:
    st.info("Upload a CSV file to begin.")
