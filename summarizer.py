import streamlit as st
from openai import OpenAI

# 🔐 Create OpenAI client using Streamlit secret
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def summarize_dataset(df):
    sample_data = df.head(5).to_string(index=False)
    prompt = f"Give a plain-English summary of this dataset:\n\n{sample_data}"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ GPT error: {e}"
