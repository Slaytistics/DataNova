import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🔄 Session State
if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🎨 Page Styling
st.set_page_config(page_title="📊 Datalicious", layout="wide")
background_image_url = "https://i.imgur.com/qo8IZvH.jpeg"
assistant_avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"

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
.element-container,
.stPlotlyChart {{
    background-color: transparent !important;
    color: black !important;
    border: none !important;
    box-shadow: none !important;
    padding: 12px;
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
html, body {{
    color: black !important;
}}
.chat-message-user {{
    background: #DCF8C6;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 6px 0;
}}
.chat-message-ai {{
    background: #EAEAEA;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 6px 0;
}}
.floating-avatar {{
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 85px;
    height: 85px;
    border-radius: 50%;
    background-image: url('{assistant_avatar_url}');
    background-size: cover;
    background-position: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 9999;
    transition: transform 0.2s ease;
}}
.floating-avatar:hover {{
    transform: scale(1.05);
}}
.chat-panel {{
    position: fixed;
    bottom: 120px;
    right: 25px;
    width: 400px;
    max-height: 500px;
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.3);
    z-index: 9998;
    padding: 20px;
    overflow-y: auto;
}}
.close-chat {{
    position: absolute;
    top: 10px;
    right: 15px;
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #666;
}}
</style>
""", unsafe_allow_html=True)

# 💬 Floating Avatar (Simplified)
def render_floating_avatar():
    components.html(f"""
    <div class="floating-avatar" title="Click to toggle chat"></div>
    """, height=0)

# Chat interaction handled through session state

# 📊 App Interface
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")
st.divider()
st.header("📁 Step 1: Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
df = None

if uploaded_file:
    try:
        # 🧼 Clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 👀 Preview
        st.subheader("👓 Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("📋 Step 2: Generate Summary")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🧠 Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.session_state["summary"] = summary
                    st.success("✅ Summary Generated!")
        with col2:
            st.markdown("This summary provides a GPT-style interpretation of your dataset.")

        if "summary" in st.session_state:
            st.markdown(f"#### 🔍 Summary Output:\n{st.session_state['summary']}")

        st.divider()
        st.header("📊 Step 3: Chart Generator")

        numeric_columns = df.select_dtypes(include=["float", "int"]).columns.tolist()
        if numeric_columns:
            with st.expander("📈 Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for charts.")

        st.divider()
        st.header("🎨 Step 4: Export to Figma")
        if "summary" in st.session_state:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("🎨 Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(st.session_state["summary"], dataset_name=dataset_name)
                    st.toast("📤 Exported to Figma!")
                    st.success(result)

        # Render floating avatar only when dataset is loaded
        render_floating_avatar()

        # Chat toggle button (main interaction)
        if st.button("💬 Toggle Chat Assistant", key="main_chat_toggle", help="Click to open/close the Q&A chat"):
            st.session_state.chatbox_open = not st.session_state.chatbox_open
            st.rerun()

        # Handle chat messages when chat is open
        if st.session_state.chatbox_open:
            st.divider()
            st.header("💬 Dataset Q&A Chat")
            
            # Input area
            col1, col2 = st.columns([3, 1])
            with col1:
                user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="main_chat_input")
            with col2:
                mode = st.selectbox("Style:", ["Normal", "ELI5", "Detailed"], key="answer_mode")
            
            if user_input:
                with st.spinner("Thinking like a data analyst..."):
                    reply = ask_dataset_question(df, user_input, mode=mode)
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("ai", reply))
                    st.rerun()
            
            # Chat history display
            if st.session_state.chat_history:
                st.subheader("Chat History")
                for role, msg in st.session_state.chat_history:
                    class_name = "chat-message-user" if role == "user" else "chat-message-ai"
                    st.markdown(f"<div class='{class_name}'><strong>{'🧑‍💻 You' if role == 'user' else '🤖 AI'}:</strong><br>{msg}</div>", unsafe_allow_html=True)
                
                # Clear chat history button
                if st.button("🗑️ Clear Chat History", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")

# Info message when no file is uploaded
else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")
