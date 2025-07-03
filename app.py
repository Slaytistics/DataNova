import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🌐 Initialize session state
if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📐 Page config
st.set_page_config(page_title="📊 Datalicious", layout="wide")
background_image_url = "https://i.imgur.com/qo8IZvH.jpeg"
avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"

# 🎨 Custom styling
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{background_image_url}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
}}

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
}}

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
</style>
""", unsafe_allow_html=True)

# 🧠 Floating avatar logic
components.html("""
<div onclick="document.getElementById('chat_toggle_button').click();" class="chat-float"></div>
<button id="chat_toggle_button" style="display:none;"></button>
""", height=0)

if st.button("💬 Toggle Assistant", key="chat_toggle_button"):
    st.session_state.chatbox_open = not st.session_state.chatbox_open

# 📁 Dataset upload
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

        # 💬 Inline Chat Assistant Panel
        if st.session_state.chatbox_open:
            st.divider()
            st.header("💬 Ask About This Dataset")
            mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
            with st.form(key="chat_form"):
                user_input = st.text_input("Ask your question:", placeholder="e.g. Which country starts with C?")
                send = st.form_submit_button("Send")
                if send and user_input:
                    with st.spinner("Thinking..."):
                        reply = ask_dataset_question(df, user_input, mode=mode)
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("ai", reply))
                    st.experimental_rerun()

            # Chat transcript
            for role, msg in st.session_state.chat_history:
                cls = "chat-message-user" if role == "user" else "chat-message-ai"
                st.markdown(f"<div class='{cls}'>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")
