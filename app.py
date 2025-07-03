import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🌄 Add background image
background_image_url = "https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg"

st.markdown(
    f"""
    <style>
    /* 🌄 Background setup */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* 🔲 Base container styling */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(0, 0, 0, 0.35) !important;
        border-radius: 12px;
        color: white !important;
    }}

    /* 📦 Common components */
    .stButton > button,
    .stFileUploader,
    .stTextInput, 
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stDataFrame,
    .stExpander,
    .stAlert,
    .stRadio,
    .element-container,
    .css-1cpxqw2,
    .css-1kyxreq {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        border-radius: 12px;
        padding: 12px;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* 🧾 Preview, markdowns, Q&A messages */
    .stMarkdown, .css-ffhzg2, .chat-message, .element-container p,
    .css-ocqkz7, .css-1y4p8pa {{
        background-color: rgba(20, 20, 20, 0.8) !important;
        color: white !important;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        text-shadow: 0 0 2px rgba(0, 0, 0, 0.6);
    }}

    /* ✍️ Input fields */
    input, textarea, select {{
        background-color: rgba(255, 255, 255, 0.07) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }}

    /* 📂 File uploader */
    [data-testid="stFileUploader"] > div {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* 🧠 Buttons */
    button[kind="primary"], .stButton > button {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: none;
        border-radius: 8px;
    }}

    /* 🧭 Expander */
    details {{
        background-color: rgba(255, 255, 255, 0.07) !important;
        border-radius: 10px;
        color: white !important;
    }}

    /* 🎚️ Slider handle */
    .stSlider > div > div > div > div {{
        background-color: #ffffff88 !important;
    }}

    /* 🎨 General text styling */
    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: white !important;
        text-shadow: 0 0 2px rgba(0, 0, 0, 0.4);
    }}

    /* 🏷️ Dropdown labels */
    label, .stSelectbox label {{
        color: #fff !important;
        font-weight: 500;
        text-shadow: 0 0 2px rgba(0,0,0,0.6);
    }}

    /* 📈 Chart area */
    .stPlotlyChart {{
        background-color: rgba(0, 0, 0, 0.2) !important;
        border-radius: 10px;
        padding: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)



# 📐 App layout and style
st.set_page_config(page_title="📊 Datalicious", layout="wide")
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")

st.divider()
st.header("📁 Step 1: Upload Your Dataset")

# 🔼 File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        # 🧼 Read and clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 👀 Dataset preview
        st.subheader("👓 Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("📋 Step 2: Generate Summary")

        # 🧠 AI summary
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

        st.divider()
        st.header("💬 Step 5: Ask About This Dataset")

        # 🧠 Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        # 🗨️ Styled chat display
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
