import streamlit as st
from figma_exporter import export_to_figma

st.title("🎨 Export to Figma")

summary = st.session_state.get("summary")
df = st.session_state.get("df")

if summary and df is not None:
    dataset_name = "Datalicious_" + str(df.shape[0]) + "_rows"
    if st.button("Export to Figma"):
        result = export_to_figma(summary, dataset_name)
        st.success(result)
else:
    st.warning("Please generate a summary first.")
