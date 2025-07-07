import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Hide Streamlit Main Menu, Footer, and Header ---
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- FontAwesome for icons ---
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True,
)

dark_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

/* Global */
body, html, div, span, label {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF !important;
    background-color: transparent !important;
    margin: 0; padding: 0;
}

/* Background */
[data-testid="stAppViewContainer"] {
    background: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg") no-repeat center center fixed;
    background-size: cover;
    min-height: 100vh;
    padding-top: 6rem;
    position: relative;
}
body::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(10, 15, 30, 0.75);
    z-index: -1;
}

/* Main Container */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 24px;
    backdrop-filter: blur(18px);
    box-shadow: 0 0 24px 3px #0b3d91;
    padding: 2rem 3rem 3rem 3rem !important;
    border: none !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6, .title-block h1, .css-10trblm {
    color: white !important;
}

/* --- BUTTONS (including Browse Files) --- */
.stButton > button,
section[data-testid="stFileUploader"] button {
    background: transparent !important;
    color: #3b82f6 !important;
    font-weight: 600;
    border-radius: 30px;
    padding: 0.6rem 2rem;
    border: 2px solid #3b82f6 !important;
    font-size: 1.05rem;
    transition: all 0.3s ease;
}
.stButton > button:hover,
section[data-testid="stFileUploader"] button:hover {
    background-color: rgba(59, 130, 246, 0.1) !important;
    color: #60a5fa !important;
    border-color: #60a5fa !important;
    box-shadow: 0 0 10px #3b82f6;
    transform: scale(1.04);
}

/* --- SELECTBOX (Dropdown) --- */
.css-1n76uvr, .css-1jqq78o, .css-1dimb5e-singleValue {
    background-color: #0a0f1a !important;
    color: #ffffff !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 12px;
}
.css-3vnyiq-option {
    background-color: #1e293b !important;
    color: #e0e0e0 !important;
    font-weight: 500;
    font-size: 1rem;
    border-bottom: 1px solid #334155;
}
.css-3vnyiq-option:hover {
    background-color: #2563eb !important;
    color: white !important;
}

/* --- Remove Blue Underline from Inputs --- */
input, textarea, .stTextInput > div > input,
.stTextArea > div > textarea,
.stPasswordInput > div > input {
    border: none !important;
    box-shadow: none !important;
    background-color: rgba(255, 255, 255, 0.06) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    outline: none !important;
}
input:focus, textarea:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Progress bar */
div[role="progressbar"] > div {
    background-color: #2563eb !important;
}

/* Chat Bubbles */
.chat-user {
    background: linear-gradient(135deg, #0a2540, #154c79);
    color: #fff;
    border-radius: 24px 24px 0 24px;
    padding: 14px 20px;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
    font-weight: 500;
    margin-bottom: 12px;
}
.chat-ai {
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: #fff;
    border-radius: 24px 24px 24px 0;
    padding: 14px 20px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
    font-weight: 500;
    margin-bottom: 12px;
}

/* Chat container */
#chat-window {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 1.5rem;
}

/* Figma container */
.figma-container {
    margin-top: 2rem;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.figma-iframe {
    width: 100%;
    height: 500px;
    border: none;
}

/* Section Header */
.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff !important;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 0.3rem;
}
</style>
"""



st.markdown(dark_css, unsafe_allow_html=True)

# --- Force All Headings to White ---
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6, .title-block h1, .css-10trblm {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<div style='text-align: center; margin-bottom: 3rem;'>
    <span style='font-size: 3rem; font-weight: 900; color: #ffffff !important; letter-spacing: 2px; margin-bottom: 0.5rem; display: block;'>DATALICIOUS</span>
    <span style='font-size: 1.2rem; color: #eee; letter-spacing: 3px; font-weight: 500;'>SLEEK. SMART. STREAMLINED.</span>
</div>
""", unsafe_allow_html=True)

# --- Figma API Integration ---
def get_figma_file(file_key, access_token):
    """Fetch Figma file using API"""
    headers = {"X-Figma-Token": access_token}
    url = f"https://api.figma.com/v1/files/{file_key}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_figma_image(file_key, access_token, node_ids=None, scale=1, format="png"):
    """Get image from Figma"""
    headers = {"X-Figma-Token": access_token}
    nodes = f"&ids={node_ids}" if node_ids else ""
    url = f"https://api.figma.com/v1/images/{file_key}?scale={scale}&format={format}{nodes}"
    response = requests.get(url, headers=headers)
    return response.json()

def embed_figma_prototype(file_key, access_token):
    """Embed Figma prototype"""
    return f"""
    <div class="figma-container">
        <iframe class="figma-iframe" src="https://www.figma.com/embed?embed_host=streamlit&url=https://www.figma.com/file/{file_key}" allowfullscreen></iframe>
    </div>
    """

# --- Figma Section ---
st.markdown('<h2 class="section-header"><i class="fa fa-paint-brush"></i> Figma Integration</h2>', unsafe_allow_html=True)

figma_access_token = st.text_input("Figma Access Token (optional)", type="password", 
                                 help="Get your access token from Figma account settings")
figma_file_key = st.text_input("Figma File Key", 
                              help="The file key from the Figma URL (e.g., for 'figma.com/file/ABC123', the key is 'ABC123')")

if figma_file_key:
    if st.button("Load Figma Design"):
        if figma_access_token:
            try:
                # Get file metadata
                file_data = get_figma_file(figma_file_key, figma_access_token)
                st.success("Figma file loaded successfully!")
                
                # Display basic info
                st.markdown(f"**Document Name:** {file_data.get('name', 'N/A')}")
                st.markdown(f"**Last Modified:** {file_data.get('lastModified', 'N/A')}")
                
                # Get and display image
                image_data = get_figma_image(figma_file_key, figma_access_token)
                if 'images' in image_data:
                    for node_id, image_url in image_data['images'].items():
                        st.image(image_url, caption=f"Figma Design - Node {node_id}")
                
            except Exception as e:
                st.error(f"Error fetching Figma data: {e}")
        else:
            st.warning("Please enter your Figma access token to fetch detailed data")
    
    # Always show the embedded prototype (works without token)
    st.markdown("### Prototype Preview")
    st.markdown(embed_figma_prototype(figma_file_key, figma_access_token), unsafe_allow_html=True)

# --- Upload Section ---
st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        st.markdown('<h2 class="section-header"><i class="fa fa-lightbulb-o"></i> Generate Summary</h2>', unsafe_allow_html=True)
        if st.button("Generate Summary"):
            with st.spinner("Calling Together AI..."):
                summary = summarize_dataset(df.head(7))
                st.success("Summary Generated!")
                st.markdown(summary)

        st.markdown('<h2 class="section-header"><i class="fa fa-bar-chart"></i> Chart Generator</h2>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            selected_column = st.selectbox("Choose column:", numeric_columns)
            top_n = st.slider("Top N values:", 5, 20, 10)
            fig = plot_top_column(df, selected_column, top_n=top_n)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        st.markdown('<h2 class="section-header"><i class="fa fa-comments"></i> Ask About This Dataset</h2>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?")
        
        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        st.markdown('<div id="chat-window">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")
