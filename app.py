import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# Initialize chat state and history
if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Page config and URLs
st.set_page_config(page_title="📊 Datalicious", layout="wide")

background_image_url = "https://i.imgur.com/qo8IZvH.jpeg"
avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"

# CSS and avatar + chat popup + hidden toggle button + JS
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{background_image_url}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
}}

.block-container {{
    padding: 2rem 3rem;
    max-width: 900px;
    margin: auto;
    background: transparent !important;
}}

.stButton > button,
.stTextInput,
.stSelectbox,
.stSlider,
.stExpander,
.stDataFrame,
.element-container {{
    background-color: transparent !important;
    color: black !important;
    border: none !important;
    box-shadow: none !important;
}}

input, textarea, select {{
    background-color: rgba(255,255,255,0.8) !important;
    color: black !important;
    border: 1px solid #ccc !important;
}}

button {{
    background-color: rgba(240,240,240,0.9) !important;
    color: black !important;
    border: 1px solid #ccc !important;
}}

.stSlider > div > div > div > div {{
    background-color: #888 !important;
}}

/* Floating avatar */
.chat-float {{
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background-image: url('{avatar_url}');
    background-size: cover;
    background-position: center;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    cursor: pointer;
    z-index: 10000;
    transition: transform 0.2s ease;
}}
.chat-float:hover {{
    transform: scale(1.1);
}}

/* Chat popup container */
.chat-popup {{
    position: fixed;
    bottom: 125px;
    right: 25px;
    width: 350px;
    max-height: 500px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    z-index: 10001;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

/* Chat popup header */
.chat-popup-header {{
    background-color: #0078D4;
    color: white;
    padding: 10px 15px;
    font-weight: bold;
    font-size: 18px;
    user-select: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

/* Close button */
.chat-popup-close {{
    cursor: pointer;
    font-size: 22px;
    font-weight: bold;
}}

/* Chat messages area */
.chat-messages {{
    flex: 1;
    padding: 10px 15px;
    overflow-y: auto;
    background: #f7f7f7;
}}

/* Message bubbles */
.chat-message-user {{
    background: #DCF8C6;
    padding: 8px 12px;
    border-radius: 15px;
    margin-bottom: 8px;
    max-width: 80%;
    align-self: flex-end;
}}

.chat-message-ai {{
    background: #EAEAEA;
    padding: 8px 12px;
    border-radius: 15px;
    margin-bottom: 8px;
    max-width: 80%;
    align-self: flex-start;
}}

/* Input area */
.chat-input-area {{
    padding: 10px 15px;
    border-top: 1px solid #ccc;
    display: flex;
    gap: 10px;
    align-items: center;
}}

.chat-input {{
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 20px;
    font-size: 14px;
    outline: none;
}}

.chat-send-button {{
    background-color: #0078D4;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: bold;
    font-size: 14px;
    transition: background-color 0.2s ease;
}}

.chat-send-button:hover {{
    background-color: #005a9e;
}}

/* Hidden toggle button */
#toggle-btn {{
    position: fixed;
    width: 1px;
    height: 1px;
    opacity: 0;
    pointer-events: none;
    user-select: none;
}}
</style>

<div class="chat-float" id="avatar" title="Toggle Chat"></div>

<script>
const avatar = document.getElementById('avatar');
const toggleBtn = document.getElementById('toggle-btn');
avatar.onclick = () => {{
    if(toggleBtn){{
        toggleBtn.click();
    }}
}};
</script>
""", unsafe_allow_html=True)

# Hidden toggle button
if st.button("Toggle Chat", key="toggle_btn"):
    st.session_state.chatbox_open = not st.session_state.chatbox_open

# Main App UI

st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")
st.divider()

st.header("📁 Upload Your Dataset")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
df = None
summary = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("👓 Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("📋 Generate Summary")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🧠 Generate Summary", key="generate_summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.session_state["summary"] = summary
                    st.success("✅ Summary Generated!")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")

        if "summary" in st.session_state:
            st.markdown(f"#### 🔍 Summary Output:\n{st.session_state['summary']}")

        st.divider()
        st.header("📊 Chart Generator")

        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("📈 Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for charts.")

        st.divider()
        st.header("🎨 Export to Figma")
        if "summary" in st.session_state:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("🎨 Export Summary to Figma", key="export_figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(st.session_state["summary"], dataset_name=dataset_name)
                    st.toast("📤 Exported to Figma!")
                    st.success(result)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")

# Chat popup UI only when toggled open
if st.session_state.chatbox_open:

    # Make sure df exists for Q&A
    if df is None:
        st.warning("Upload and load a dataset first to ask questions.")
    else:

        st.markdown("""
        <div class="chat-popup" id="chat-popup">
            <div class="chat-popup-header">
                💬 AI Data Chat
                <span id="chat-close" class="chat-popup-close" style="cursor:pointer;">&times;</span>
            </div>
        """, unsafe_allow_html=True)

        # Chat messages container
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f'<div class="chat-message-user">{msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-ai">{msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Chat input and send button
        user_question = st
