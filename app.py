import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column  # Make sure this now accepts `top_n` parameter

# 🖥️ Page setup
st.set_page_config(page_title="📊 Datalicious — AI Data Summary", layout="centered")
st.title("🎉 Datalicious")
st.markdown("Upload structured data and generate GPT-style summaries & charts. No code needed! ✨")

# 📂 File Upload
uploaded_file = st.file_uploader("📁 Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # 🔍 Read and clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]

        # 🔢 Attempt to convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("📄 Dataset Preview:")
        st.dataframe(df.head())

        # 🤖 AI Summary from Together AI
        if st.button("🧠 Generate AI Summary"):
            with st.spinner("Calling Together AI..."):
                summary = summarize_dataset(df.head(7))
                st.success("✅ Summary Ready!")
                st.markdown(f"### 📋 Summary\n{summary}")

        # 📈 Interactive Plotly Chart
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

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Upload a CSV file to get started.")
