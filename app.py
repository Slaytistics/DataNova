import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# Session State Initialization
def init_session_state():
    if "chatbox_open" not in st.session_state:
        st.session_state.chatbox_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = ""
    if "summary" not in st.session_state:
        st.session_state.summary = None

# Page Configuration
def configure_page():
    st.set_page_config(page_title="📊 Datalicious", layout="wide")
    st.markdown("""
        <style>
            /* Add your CSS styles here */
        </style>
    """, unsafe_allow_html=True)

# Floating Chat Widget
def render_floating_chat_widget():
    # Your chat widget HTML and JavaScript code here
    components.html("""
        <!-- Your chat widget HTML here -->
        <script>
            // Your JavaScript code here
        </script>
    """, height=0)

# Main Application
def main():
    init_session_state()
    configure_page()

    st.title("📊 Datalicious — AI Data Assistant")
    st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")
    st.divider()

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = clean_dataset(df)

            st.subheader("👓 Preview")
            st.dataframe(df.head(), use_container_width=True)

            st.divider()
            st.header("📋 Step2: Generate Summary")

            col1, col2 = st.columns([1,3])
            with col1:
                if st.button("🧠 Generate Summary"):
                    with st.spinner("Calling Together AI..."):
                        summary = summarize_dataset(df.head(7))
                        st.session_state["summary"] = summary
                        st.success("✅ Summary Generated!")
            with col2:
                st.markdown("This summary provides a GPT-style interpretation of your dataset.")

            if st.session_state["summary"] is not None:
                st.markdown(f"#### 🔍 Summary Output:\n{st.session_state['summary']}")

            st.divider()
            st.header("📊 Step3: Chart Generator")

            numeric_columns = df.select_dtypes(include=["float", "int"]).columns.tolist()
            if numeric_columns:
                with st.expander("📈 Chart Controls", expanded=True):
                    selected_column = st.selectbox("Choose column:", numeric_columns)
                    top_n = st.slider("Top N values:", 5, 20, 10)
                    fig = plot_top_column(df, selected_column, top_n=top_n)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No numeric columns found for charts.")

            st.divider()
            st.header("🎨 Step4: Export to Figma")
            if st.session_state["summary"] is not None:
                dataset_name = uploaded_file.name.split(".")[0]
                if st.button("🎨 Export Summary to Figma"):
                    with st.spinner("Sending to Figma..."):
                        result = export_to_figma(st.session_state["summary"], dataset_name=dataset_name)
                        st.toast("📤 Exported to Figma!")
                        st.success(result)

            render_floating_chat_widget()
            handle_js_events(df)

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")

    else:
        st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")

def clean_dataset(df):
    df.columns = [col.strip() for col in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

def handle_js_events(df):
    # Handle incoming messages from JavaScript
    message = st.experimental_get_query_params().get('message', [None])[0]
    if message:
        st.session_state.pending_question = message

    if st.session_state.pending_question:
        user_question = st.session_state.pending_question
        st.session_state.pending_question = ""
        
        with st.spinner("AI is thinking..."):
            ai_response = ask_dataset_question(df, user_question, mode="Normal")
            st.session_state.chat_history.append(("user", user_question))
            st.session_state.chat_history.append(("ai", ai_response))
            
        st.components.v1.html(f"""
            <script>
                window.parent.postMessage({{
                    type: 'ai-response',
                    message: `{ai_response.replace('`', '\\`').replace('"', '\\"')}`
                }}, '*');
            </script>
        """, height=0)

if __name__ == "__main__":
    main()
