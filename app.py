import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 💬 Chat state initialization
if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🌄 Background + avatar styling
st.set_page_config(page_title="📊 Datalicious", layout="wide")
background_image_url = "https://i.imgur.com/qo8IZvH.jpeg"
avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"

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

    /* Widget transparency */
    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .stDataFrame,
    .element-container,
    .stPlotlyChart,
    .chat-message,
    details {{
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

    .stSlider > div > div > div > div {{
        background-color: #888 !important;
    }}

    /* Floating avatar */
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
""", unsafe_allow_html=True)

# 🧠 Floating chat trigger
components.html(f"""
    <div onclick="document.getElementById('chat_toggle_button').click();" class="chat-float"></div>
    <button id="chat_toggle_button" style="display:none;"></button>
""", height=0)

if st.button("💬 Click to Chat", key="chat_toggle"):
    st.session_state.chatbox_open = not st.session_state.chatbox_open

# ✅ Main App
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")
st.divider()
st.header("📁 Step 1: Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

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
        st.header("📋 Step 2: Generate Summary")
        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🧠 Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("✅ Summary Generated!")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")

        if summary:
            st.markdown(f"#### 🔍 Summary Output:\n{summary}")

        st.divider()
        st.header("📊 Step 3: Chart Generator")

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
        st.header("🎨 Step 4: Export to Figma")
        if summary:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("🎨 Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(summary, dataset_name=dataset_name)
                    st.toast("📤 Exported to Figma!")
                    st.success(result)

        # 💬 Chat Section (Toggled)
        if st.session_state.chatbox_open:
            st.divider()
            st.header("💬 Step 5: Ask About This Dataset")

            mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
            user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

            if user_input:
                with st.spinner("Thinking like a data analyst..."):
                    reply = ask_dataset_question(df, user_input, mode=mode)
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("ai", reply))

            for role, msg in st.session_state.chat_history:
                bg = "#DCF8C6" if role == "user" else "#EAEAEA"
                prefix = "🧑‍💻 You:" if role == "user" else "🤖 AI:"
                st.markdown(
                    f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px'><strong>{prefix}</strong><br>{msg}</div>",
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")
