import streamlit as st
import requests

def ask_dataset_question(df, question, mode="Normal"):
    api_key = st.secrets["TOGETHER_API_KEY"]


    try:
        sample_data = df.sample(min(20, len(df)), random_state=42).to_string(index=False)
    except Exception:
        sample_data = "Not available."

 
    try:
        stats = df.describe(include='all').to_string()
    except Exception:
        stats = "Not available."

   
    try:
        missing_counts = df.isnull().sum().to_string()
    except Exception:
        missing_counts = "Not available."

  
    try:
        dtypes_info = df.dtypes.to_string()
    except Exception:
        dtypes_info = "Not available."

  
    style_hint = {
        "Explain like I'm 5": "Explain in simple and beginner-friendly terms.",
        "Detailed": "Provide a detailed and technical answer for advanced users.",
        "Normal": ""
    }.get(mode, "")

   
    prompt = f"""You're a helpful data analyst assisting the user.

== Sample Rows ==
{sample_data}

== Summary Stats ==
{stats}

== Missing Value Counts ==
{missing_counts}

== Column Data Types ==
{dtypes_info}

The user asked: "{question}"

{style_hint}

Answer clearly and accurately, using only the dataset shown above."""

    # 🔐 API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"
