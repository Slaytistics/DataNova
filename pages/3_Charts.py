import streamlit as st
from visualizer import plot_top_column

st.title("📊 Chart Generator")

df = st.session_state.get("df")
if df is not None:
    num_cols = df.select_dtypes(include=["float", "int"]).columns
    col = st.selectbox("Column to plot:", num_cols)
    top_n = st.slider("Top N values:", 5, 20, 10)
    fig = plot_top_column(df, col, top_n)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please upload a dataset first.")
