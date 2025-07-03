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
    /* 🌌 Background */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* 🔲 Main UI components */
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
    .css-1kyxreq,
    .css-1cpxqw2 {{
        background-color: rgba(0, 0, 0, 0.35) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}

    /* ✅ Input fields (clean + spaced) */
    input, textarea, select {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        font-size: 16px !important;
    }}

    /* 📂 File uploader inner box */
    [data-testid="stFileUploader"] > div {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px;
        padding: 12px !important;
        border: 1px solid rgba(255,255,255,0.15);
    }}

    /* 💬 Chat-like messages */
    .chat-message {{
        background-color: rgba(255, 255, 255, 0.07);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
    }}

    /* ✨ Text color */
    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: white !important;
    }}

    /* 🎛️ Slider knob */
    .stSlider > div > div > div > div {{
        background-color: #ffffff88 !important;
    }}

    /* 🧠 Buttons */
    button[kind="primary"], .stButton > button {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: white !important;
        border: none !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
    }}

    /* 📈 Charts */
    .stPlotlyChart {{
        background-color: rgba(0, 0, 0, 0.25) !important;
        border-radius: 10px;
        padding: 8px;
    }}

    /* 🧭 Expander */
    details {{
        background-color: rgba(255, 255, 255, 0.07) !important;
        border-radius: 10px;
        color: white !important;
        padding: 10px;
    }}

    /* 🧊 General layout */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* 🔄 Fix text cutoff on selectboxes & inputs */
    .stTextInput > div > input,
    .stSelectbox > div > div {{
        padding: 12px 16px !important;
        font-size: 16px !important;
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
