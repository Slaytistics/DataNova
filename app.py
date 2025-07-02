from summarizer import summarize_dataset
from visualizer import plot_top_column
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 🔐 Load API key from secrets.toml
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# 🔍 GPT summary function using OpenRouter API
def summarize_dataframe(df):
    try:
        sample_data = df.head(5).to_string(index=False)
        prompt = f"Summarize this dataset in plain English:\n\n{sample_data}"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/yourgithub",  # Optional: add your repo link
            "X-Title": "student-gpt4-infographic",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "❌ GPT error: " + str(result)
    except Exception as e:
        return f"❌ Something went wrong: {e}"

# 🖥️ Streamlit App UI
st.set_page_config(page_title="AI Dataset Summary Chatbot", layout="centered")
st.title("📊 AI-Powered Dataset Chatbot (GPT-4 Style)")
st.markdown("Upload a CSV file and get a summary & chart using AI ✨")

# 📂 File Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📁 Preview of Dataset:")
        st.dataframe(df.head())

        # 🧠 GPT Summary
        if st.button("🧠 Generate GPT Summary"):
            with st.spinner("Talking to GPT..."):
                summary = summarize_dataframe(df)
                st.success("✅ Summary Ready!")
                st.markdown(f"📋 **Summary**:\n\n{summary}")

        # 📊 Infographic
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()

        if numeric_columns:
            selected_column = st.selectbox("📊 Select numeric column to visualize:", numeric_columns)
            if selected_column:
                fig = px.bar(
                    df.sort_values(by=selected_column, ascending=False).head(10),
                    x=df.columns[0],
                    y=selected_column,
                    title=f"Top 10 {df.columns[0]} by {selected_column}"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No numeric columns found for chart generation.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("⬆️ Upload a CSV file to get started.")

if _name_ == "_main_":
    main()
