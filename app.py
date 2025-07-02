import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🖥️ Page setup
st.set_page_config(page_title="📊 Datalicious — AI Data Summary", layout="centered")
st.title("🎉 Datalicious")
st.markdown("Upload structured data and generate GPT-style summaries, visual charts, and even export designs to Figma. No code needed! ✨")

# 📂 File Upload
uploaded_file = st.file_uploader("📁 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # 🔍 Read and clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("📄 Dataset Preview")
        st.dataframe(df.head())

        # 🤖 AI Summary
        summary = None
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Calling Together AI..."):
                summary = summarize_dataset(df.head(7))
                st.success("✅ Summary Ready!")
                st.markdown(f"### 📋 Summary\n{summary}")

        # 🎨 Export to Figma
        if summary:
            if st.button("🎨 Export to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(summary)
                    st.success(result)

        # 📈 Interactive Chart Generator
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            st.markdown("### 📊 Infographic Generator")
            selected_column = st.selectbox("Choose a numeric column:", numeric_columns)
            top_n = st.slider("Top N rows to display:", min_value=5, max_value=20, value=10)
            if selected_column:
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for chart generation.")

        # 💬 AI Q&A Chat Interface
        st.markdown("### 💬 Ask About This Dataset")

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # 🎯 Answer style selector
        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])

        # 💬 User question input
        user_input = st.text_input(
            "Your question:",
            placeholder="e.g. What is the average salary?",
            key="qna_input"
        )

        # 💡 Ask and respond
        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        # 🧠 Display chat history
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"🧑‍💻 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

else:
    st.info("⬆️ Upload a CSV file to get started.")
