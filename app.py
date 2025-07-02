import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 🔑 Your OpenRouter API key (replace with your real key)
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# 🧠 GPT summary using OpenRouter (Mistral model)
def summarize_dataframe(df):
    sample_data = df.head(5).to_string(index=False)
    prompt = f"Summarize this dataset in plain English:\n\n{sample_data}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/yourgithub",  # Replace with your GitHub or localhost
        "X-Title": "student-gpt4-infographic",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",  # Free GPT-4 alternative
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ API Error:\n{result}"

# 🖥️ Streamlit App UI
st.set_page_config(page_title="AI Dataset Summary Chatbot", layout="centered")
st.title("📊 AI-Powered Dataset Chatbot (GPT-4 Style)")
st.markdown("Upload a CSV and get a GPT-style text summary + chart ✨")

# File Upload
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📁 Preview of Dataset:")
    st.dataframe(df.head())

    # Summary
    if st.button("🧠 Generate GPT Summary"):
        with st.spinner("Talking to GPT..."):
            summary = summarize_dataframe(df)
            st.success("✅ Summary Ready!")
            st.markdown(f"📋 Summary:\n\n{summary}")

    # Infographic
    if st.button("📈 Generate Infographic"):
        numeric_columns = df.select_dtypes(include=['float64', 'int64', 'int32']).columns.tolist()
        if not numeric_columns:
            st.error("⚠️ No numeric columns found for chart.")
        else:
            selected_column = st.selectbox("📊 Select numeric column to visualize:", numeric_columns)
            fig = px.bar(df.sort_values(by=selected_column, ascending=False).head(10),
                         x=df.columns[0], y=selected_column,
                         title=f"Top 10 {df.columns[0]} by {selected_column}")
            st.plotly_chart(fig, use_container_width=True)
