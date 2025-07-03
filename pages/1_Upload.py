import streamlit as st
import pandas as pd

st.title("📁 Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]
    st.session_state["df"] = df
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())
