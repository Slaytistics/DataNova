import streamlit as st
from qna import ask_dataset_question

st.title("💬 Ask About This Dataset")

df = st.session_state.get("df")
if df is not None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
    user_input = st.text_input("Ask a question:", placeholder="e.g. Which country starts with C?")
    if user_input:
        reply = ask_dataset_question(df, user_input, mode=mode)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("ai", reply))

    for role, msg in st.session_state.chat_history:
        bg = "#DCF8C6" if role == "user" else "#EAEAEA"
        prefix = "🧑‍💻 You:" if role == "user" else "🤖 AI:"
        st.markdown(f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px'><strong>{prefix}</strong><br>{msg}</div>", unsafe_allow_html=True)
else:
    st.warning("Please upload a dataset first.")
