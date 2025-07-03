import streamlit as st
import pandas as pd
from qna import ask_dataset_question  # Ensure this function exists

# 🖼️ Configure layout
st.set_page_config(page_title="📊 Datalicious", layout="centered")

# 🌄 Images
avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"
background_url = "https://i.imgur.com/xlx2V3C.jpeg"

# 🧠 Floating avatar CSS
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url('{background_url}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .transbox {{
        background-color: rgba(255,255,255,0.85);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 2px 12px rgba(0,0,0,0.2);
    }}
    .chat-float {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background-image: url('{avatar_url}');
        background-size: cover;
        background-position: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        z-index: 9999;
    }}
    </style>
    <div class="chat-float"></div>
""", unsafe_allow_html=True)

# 🕹️ Invisible button (positioned where avatar is rendered)
if st.button("💬 Click to Chat", key="chat_toggle"):
    st.session_state.chatbox_open = True

if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False

# 📦 Translucent main content box
st.markdown("<div class='transbox'>", unsafe_allow_html=True)

st.image("https://i.imgur.com/gdSdfhT.png", width=120)
st.title("📊 Datalicious")
st.subheader("Your AI-powered data design assistant")
st.markdown("Turn raw CSVs into summaries, visualizations, and export-ready designs — effortlessly.")

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 📋 Summary")
    st.caption("Generate GPT-style insights from structured data.")
with col2:
    st.markdown("### 📊 Charts")
    st.caption("Create sleek visualizations with one click.")
with col3:
    st.markdown("### 🎨 Figma Export")
    st.caption("Send summaries directly to your Figma design file.")

st.markdown("---")
st.page_link("pages/1_Upload.py", label="🚀 Upload Your CSV", icon="📁")
st.caption("Crafted by Sargam • Powered by Together AI + Streamlit + Figma")
st.markdown("</div>", unsafe_allow_html=True)

# 💬 Inline Chat Assistant Panel
if st.session_state.chatbox_open:
    st.markdown("### 🤖 AI Chat Assistant")
    df = st.session_state.get("df") or pd.DataFrame()
    user_question = st.text_input("Ask me something:", key="bubble_input")
    if user_question:
        reply = ask_dataset_question(df, user_question, mode="Normal")
        st.markdown(f"🧑‍💻 **You:** {user_question}")
        st.markdown(f"🤖 **AI:** {reply}")
