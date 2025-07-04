import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# --- Load Font Awesome for icons ---
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
    unsafe_allow_html=True,
)

# --- Initialize session state for theme ---
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
    st.session_state.theme_selector = "Dark"


def set_theme(theme_name):
    st.session_state.theme = theme_name
    st.session_state.theme_selector = theme_name


# --- CSS for Neon, Glassmorphism, and Layout ---
dark_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

body, html, div, span, label {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF !important;
    background-color: #0f0f15 !important;
    margin: 0; padding: 0;
}

/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    min-height: 100vh;
    padding-top: 4rem;
    position: relative;
}

/* Neon glow container */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    backdrop-filter: blur(16px);
    box-shadow: 0 0 20px 2px #ff69b4, 0 0 40px 6px #9b30ff;
    padding: 2rem 3rem 3rem 3rem !important;
}

/* Sticky top bar */
#top-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3.5rem;
    background: #12121f;
    box-shadow: 0 0 12px #ff69b4;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    z-index: 9999;
    font-weight: 700;
    font-size: 1.4rem;
    color: #ff69b4;
    letter-spacing: 2px;
    user-select: none;
}

/* Neon button */
.stButton > button {
    background: linear-gradient(45deg, #9B30FF, #FF69B4);
    color: white !important;
    font-weight: 700;
    border-radius: 30px;
    padding: 0.7rem 2.5rem;
    box-shadow: 0 0 8px #FF69B4, 0 0 20px #9B30FF;
    transition: all 0.3s ease;
    border: none !important;
    font-size: 1.1rem;
}
.stButton > button:hover {
    box-shadow: 0 0 12px #FF69B4, 0 0 30px #9B30FF;
    transform: scale(1.05);
}

/* Input and select styling */
.stTextInput > div > input,
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    border: 1.5px solid transparent !important;
    color: #fff !important;
    padding: 0.6rem 1rem !important;
    font-size: 1rem !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.stTextInput > div > input:focus,
.stSelectbox > div > div:focus {
    border-color: #ff69b4 !important;
    box-shadow: 0 0 12px #ff69b4 !important;
    outline: none !important;
}

/* Select dropdown menu */
div[data-baseweb="menu"] {
    background: rgba(40, 20, 40, 0.95) !important;
    border-radius: 20px !important;
    border: 1px solid #ff69b4 !important;
    box-shadow: 0 0 20px #ff69b4 !important;
}
div[data-baseweb="menu"] div[role="option"] {
    color: #fff !important;
    padding: 12px 16px !important;
}
div[data-baseweb="menu"] div[role="option"]:hover {
    background: #ff69b4 !important;
    color: #0f0f15 !important;
}

/* Dataframe styling */
.stDataFrame table {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #fff !important;
    border-radius: 16px;
    box-shadow: 0 0 12px #9b30ff;
}

/* Plotly chart container */
.js-plotly-plot .plotly {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 20px;
    box-shadow: 0 0 20px #ff69b4;
}

/* Card style for sections */
.card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px 0 rgba(255, 105, 180, 0.37);
    padding: 2rem;
    margin-bottom: 2.5rem;
    border: 1px solid rgba(255, 105, 180, 0.3);
}

/* Section headers with neon underline */
.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #ff69b4;
    margin-bottom: 1rem;
    position: relative;
    letter-spacing: 1.5px;
}
.section-header::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -6px;
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #9b30ff, #ff69b4);
    border-radius: 4px;
}

/* Chat bubbles with gradient and shadows */
.chat-user {
    background: linear-gradient(135deg, #00ffff, #32cd32);
    color: #000;
    border-radius: 24px 24px 0 24px;
    padding: 14px 20px;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(0, 255, 255, 0.5);
    font-weight: 600;
    margin-bottom: 12px;
    word-wrap: break-word;
}
.chat-ai {
    background: linear-gradient(135deg, #ff69b4, #9b30ff);
    color: #fff;
    border-radius: 24px 24px 24px 0;
    padding: 14px 20px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 16px rgba(255, 105, 180, 0.5);
    font-weight: 600;
    margin-bottom: 12px;
    word-wrap: break-word;
}

/* Chat container with scroll */
#chat-window {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 1.5rem;
}

/* Horizontal scroll container for charts or summaries */
.horizontal-scroll {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 1.5rem;
    padding-bottom: 1rem;
}
.horizontal-scroll > div {
    scroll-snap-align: start;
    flex: 0 0 auto;
    width: 320px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 0 20px #ff69b4;
}

/* Dark mode toggle switch */
.toggle-switch {
    cursor: pointer;
    background: #222;
    border-radius: 30px;
    width: 50px;
    height: 26px;
    position: relative;
    box-shadow: 0 0 8px #ff69b4;
    transition: background 0.3s ease;
}
.toggle-switch::before {
    content: "";
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    background: #ff69b4;
    border-radius: 50%;
    transition: transform 0.3s ease;
    box-shadow: 0 0 12px #ff69b4;
}
.toggle-switch.active {
    background: #ff69b4;
}
.toggle-switch.active::before {
    transform: translateX(24px);
}

/* Utility spacing */
.mt-2 { margin-top: 1rem !important; }
.mb-2 { margin-bottom: 1rem !important; }
/* Fix selectbox and input placeholder color in dark mode */
.stSelectbox div[data-baseweb="select"] input,
.stSelectbox div[data-baseweb="select"] div[role="option"] {
    color: #fff !important;
    opacity: 1 !important;
}

.stSelectbox div[data-baseweb="select"] {
    color: #fff !important;
}

/* Fix placeholder visibility */
.stSelectbox input::placeholder,
.stTextInput input::placeholder {
    color: #ccc !important;
    opacity: 0.8 !important;
}

</style>
"""

light_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

body, html, div, span, label {
    font-family: 'Poppins', sans-serif !important;
    color: #222 !important;
    background-color: #f9f9f9 !important;
    margin: 0; padding: 0;
}

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f0f0, #dcdcdc);
    min-height: 100vh;
    padding-top: 4rem;
    position: relative;
}

/* Container */
.block-container {
    max-width: 900px;
    margin: auto;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    box-shadow: 0 0 12px rgba(0,0,0,0.1);
    padding: 2rem 3rem 3rem 3rem !important;
    color: #222 !important;
}

/* Sticky top bar */
#top-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3.5rem;
    background: #fff;
    box-shadow: 0 0 12px #ccc;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    z-index: 9999;
    font-weight: 700;
    font-size: 1.4rem;
    color: #9b30ff;
    letter-spacing: 2px;
    user-select: none;
}

/* Button */
.stButton > button {
    background: linear-gradient(45deg, #9B30FF, #FF69B4);
    color: white !important;
    font-weight: 700;
    border-radius: 30px;
    padding: 0.7rem 2.5rem;
    box-shadow: 0 0 8px #FF69B4, 0 0 20px #9B30FF;
    transition: all 0.3s ease;
    border: none !important;
    font-size: 1.1rem;
}
.stButton > button:hover {
    box-shadow: 0 0 12px #FF69B4, 0 0 30px #9B30FF;
    transform: scale(1.05);
}

/* Input and select styling */
.stTextInput > div > input,
.stSelectbox > div > div {
    background: #fff !important;
    border-radius: 20px !important;
    border: 1.5px solid #ddd !important;
    color: #222 !important;
    padding: 0.6rem 1rem !important;
    font-size: 1rem !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.stTextInput > div > input:focus,
.stSelectbox > div > div:focus {
    border-color: #9b30ff !important;
    box-shadow: 0 0 12px #9b30ff !important;
    outline: none !important;
}

/* Select dropdown menu */
div[data-baseweb="menu"] {
    background: #fff !important;
    border-radius: 20px !important;
    border: 1px solid #9b30ff !important;
    box-shadow: 0 0 20px #9b30ff !important;
}
div[data-baseweb="menu"] div[role="option"] {
    color: #222 !important;
    padding: 12px 16px !important;
}
div[data-baseweb="menu"] div[role="option"]:hover {
    background: #9b30ff !important;
    color: #fff !important;
}

/* Dataframe styling */
.stDataFrame table {
    background: #fff !important;
    color: #222 !important;
    border-radius: 16px;
    box-shadow: 0 0 12px #9b30ff;
}

/* Plotly chart container */
.js-plotly-plot .plotly {
    background: #fff !important;
    border-radius: 20px;
    box-shadow: 0 0 20px #9b30ff;
}

/* Card style for sections */
.card {
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 8px 32px 0 rgba(155, 48, 255, 0.37);
    padding: 2rem;
    margin-bottom: 2.5rem;
    border: 1px solid rgba(155, 48, 255, 0.3);
    color: #222 !important;
}

/* Section headers with underline */
.section-header {
    font-size: 2rem;
    font-weight: 700;
    color: #9b30ff;
    margin-bottom: 1rem;
    position: relative;
    letter-spacing: 1.5px;
}
.section-header::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -6px;
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #9b30ff, #ff69b4);
    border-radius: 4px;
}

/* Chat bubbles */
.chat-user {
    background: linear-gradient(135deg, #00ffff, #32cd32);
    color: #000;
    border-radius: 24px 24px 0 24px;
    padding: 14px 20px;
    max-width: 75%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(0, 255, 255, 0.5);
    font-weight: 600;
    margin-bottom: 12px;
    word-wrap: break-word;
}
.chat-ai {
    background: linear-gradient(135deg, #9b30ff, #ff69b4);
    color: #fff;
    border-radius: 24px 24px 24px 0;
    padding: 14px 20px;
    max-width: 75%;
    margin-right: auto;
    box-shadow: 0 4px 16px rgba(155, 48, 255, 0.5);
    font-weight: 600;
    margin-bottom: 12px;
    word-wrap: break-word;
}

/* Chat container */
#chat-window {
    max-height: 360px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 1.5rem;
}

/* Horizontal scroll container */
.horizontal-scroll {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    gap: 1.5rem;
    padding-bottom: 1rem;
}
.horizontal-scroll > div {
    scroll-snap-align: start;
    flex: 0 0 auto;
    width: 320px;
    background: #fff;
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 0 20px #9b30ff;
}

/* Utility spacing */
.mt-2 { margin-top: 1rem !important; }
.mb-2 { margin-bottom: 1rem !important; }
</style>
"""

# You can add more themes here if desired
themes = {
    "Dark": dark_css,
    "Light": light_css,
}

# Apply selected theme CSS
st.markdown(themes[st.session_state.theme], unsafe_allow_html=True)

# --- Top Bar with Theme Selector ---
with st.container():
    st.markdown(
        """
        <div id="top-bar">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap: 1rem;">
                    <i class="fa fa-database" style="font-size:1.8rem; color:#ff69b4;"></i>
                    <span style="font-size:1.4rem; font-weight:700; color:#ff69b4;">DATALICIOUS</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)  # spacing for visibility

with st.container():
    col1, col2 = st.columns([6, 2])
    with col1:
        st.markdown("""
            <div id="top-bar">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap: 1rem;">
                        <i class="fa fa-database" style="font-size:1.8rem; color:#ff69b4;"></i>
                        <span style="font-size:1.4rem; font-weight:700; color:#ff69b4;">DATALICIOUS</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        selected_theme = st.selectbox(
            "🎨 Theme",
            options=list(themes.keys()),
            index=list(themes.keys()).index(st.session_state.theme),
            key="theme_selector"
        )
        if selected_theme != st.session_state.theme:
            set_theme(selected_theme)
            st.experimental_rerun()



# Handle theme change via query params
query_params = st.experimental_get_query_params()
if "theme" in query_params:
    selected_theme = query_params["theme"][0]
    if selected_theme in themes:
        set_theme(selected_theme)
        st.experimental_set_query_params()  # clear params
        st.experimental_rerun()

# --- Main Content Container ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Upload Section
    st.markdown('<h2 class="section-header"><i class="fa fa-upload"></i> Upload Your Dataset</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if not uploaded_file:
        st.info("Upload a CSV file to begin your Datalicious journey.")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # Preview Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header"><i class="fa fa-table"></i> Preview</h2>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Summary Section with horizontal scroll
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header"><i class="fa fa-lightbulb-o"></i> Generate Summary</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        summary = None
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated! 🎉")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")
        if summary:
            st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)
            st.markdown(f'<div>{summary}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart Generator Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header"><i class="fa fa-bar-chart"></i> Chart Generator</h2>', unsafe_allow_html=True)
        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)
                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": True,
                        "scrollZoom": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["sendDataToCloud"],
                    }
                )
        else:
            st.warning("No numeric columns found for charts.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Q&A Chat Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header"><i class="fa fa-comments"></i> Ask About This Dataset</h2>', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

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

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")












