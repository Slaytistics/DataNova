# 🔽 Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px

# 💡 Custom modules
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# ⚙️ Set Streamlit page configuration
st.set_page_config(page_title="Datalicious", layout="wide")

# 🖼️ Full-width banner image
st.markdown("""
    <div style="width: 100%; margin-top: -2rem;">
        <img src="https://i.imgur.com/Sq8U7cY.png" style="width: 100%; height: auto; display: block; margin-bottom: -1rem;" />
    </div>
""", unsafe_allow_html=True)

# 🎨 Custom styles
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://i.imgur.com/qo8IZvH.jpeg");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        font-family: Arial;
        font-style: italic;
    }
    .block-container {
        padding: 2rem 3rem;
        max-width: 900px;
        margin: auto;
        background: transparent !important;
        font-family: Arial;
        font-style: italic;
    }
    .stButton > button {
        background: linear-gradient(90deg, #ff69b4, #ff1493);
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(255, 20, 147, 0.6);
        transition: all 0.3s ease;
        cursor: pointer;
        font-family: Arial;
        font-style: italic;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #ff1493, #ff69b4);
        box-shadow: 0 6px 14px rgba(255, 20, 147, 0.8);
    }
    input, textarea, select {
        background-color: rgba(255,255,255,0.85) !important;
        color: #222 !important;
        border: 1px solid #bbb;
        border-radius: 6px;
        font-family: Arial;
        font-style: italic;
    }
    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #222 !important;
        font-family: Arial;
        font-style: italic;
    }
    h1, .stTitle { color: #FF0000; }
    h2, .stHeader { color: #FF0000; }
    h3 { color: #0000FF; }
    h4 { color: #FF00FF; }
    h5 { color: #800080; }
    h6 { color: #C71585; }
    .chat-user {
        background: #FADADD;
        padding: 10px;
        border-radius: 8px;
        margin: 6px;
    }
    .chat-ai {
        background: #E6E6FA;
        padding: 10px;
        border-radius: 8px;
        margin: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# 📢 App intro
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma")

# 📁 File upload
st.divider()
st.header("Upload Your Dataset")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # 🧼 Clean the data
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 👀 Preview section
        st.subheader("Preview")
        st.dataframe(df.head(), use_container_width=True)

        # 🧠 Summary generator
        st.divider()
        st.header("Generate Summary")
        if "summary" not in st.session_state:
            st.session_state.summary = None

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    st.session_state.summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated!")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")
        if st.session_state.summary:
            st.markdown(f"#### Summary Output:\n{st.session_state.summary}")

        # 📊 Chart visualizer
        st.divider()
        st.header("Chart Generator")
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        # 🎨 Figma export
        st.divider()
        st.header("Export to Figma")
        if st.session_state.summary:
            dataset_name = uploaded_file.name.rsplit(".", 1)[0]
            if st.button("Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(st.session_state.summary, dataset_name=dataset_name)
                    st.toast("Exported to Figma!")
                    st.success(result)

        # 💬 Q&A chatbot
        st.divider()
        st.header("Ask About This Dataset")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.extend([("user", user_input), ("ai", reply)])

        # 🔄 Chat display
        for role, msg in st.session_state.chat_history:
            div_class = "chat-user" if role == "user" else "chat-ai"
            st.markdown(f"<div class='{div_class}'><strong>{role.capitalize()}:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("📂 Please upload a CSV file to start exploring your data with Datalicious.")
