# qna.py
import streamlit as st
import requests

def ask_dataset_question(df, question):
    api_key = st.secrets["TOGETHER_API_KEY"]
    sample_data = df.head(10).to_string(index=False)

    prompt = f"""
You are a smart and friendly data analyst helping a user explore a dataset. Here is a sample of their data:
{sample_data}


The user asked: "{question}"

Give a clear, accurate, and helpful answer based only on the provided dataset.
"""
