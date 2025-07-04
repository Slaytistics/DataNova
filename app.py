import streamlit as st
import pandas as pd
import plotly.express as px
from summarizer import summarize_dataset
from visualizer import plot_top_column
from qna import ask_dataset_question

# Custom styles with Inter font, dark theme, and background image
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.pexels.com/photos/2098427/pexels-photo-2098427.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=1080");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
    padding: 0rem 2rem 1.5rem 2rem !important;
    max-width: 800px;
    margin: auto;
    }

    /* Transparent background for text containers */
    .stMarkdown, .stText, .stHeading, .stSubheader, .stCaption, .stCodeBlock {
        background-color: transparent !important;
        padding: 4px 0px !important;
        border: none !important;
        margin-bottom: 0.6rem;
        backdrop-filter: none !important;
    }

    /* Other interactive elements */
    .stButton > button,
    .stFileUploader,
    .stTextInput,
    .stSelectbox,
    .stSlider,
    .stTextArea,
    .stRadio,
    .stExpander,
    .element-container,
    .stPlotlyChart,
    .chat-message,
    details {
        background-color: rgba(15, 15, 15, 0.3) !important;
        color: #f0f0f0 !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        padding: 10px !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(2px);
    }

    input, textarea, select {
        background-color: rgba(30, 30, 30, 0.9) !important;
        color: #f0f0f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 6px;
        padding: 6px !important;
    }

    button {
        background-color: rgba(60, 60, 60, 0.85) !important;
        color: #f0f0f0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        transition: background-color 0.3s ease;
    }

    button:hover {
        background-color: rgba(80, 80, 80, 1) !important;
    }

    html, body, h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #f0f0f0 !important;
        font-family: 'Inter', sans-serif;
    }

    .element-container {
        margin-bottom: 0.6rem !important;
    }

    .js-plotly-plot .plotly {
        background-color: rgba(15,15,15,0.6) !important;
    }

    .stDataFrame {
        background-color: rgba(15,15,15,0.6) !important;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .stDataFrame table {
        background-color: rgba(15,15,15,0.6) !important;
        color: #f0f0f0 !important;
    }

    .stSlider > div > div > div > div {
        background-color: #cccccc33 !important;
    }
       /* --- Dark dropdowns (st.selectbox) --- */
[data-baseweb="select"] {
    background-color: rgba(25, 25, 25, 0.85) !important;
    color: #f0f0f0 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
}

[data-baseweb="select"] * {
    color: #f0f0f0 !important;
    background-color: rgba(25, 25, 25, 0.9) !important;
}

div[role="listbox"] {
    background-color: rgba(20, 20, 20, 0.95) !important;
    color: white !important;
    border-radius: 8px !important;
}

div[role="option"]:hover {
    background-color: rgba(50, 50, 50, 0.9) !important;
}
/* Dark dropdown list when expanded */
div[role="listbox"] {
    background-color: rgba(15, 15, 15, 0.95) !important;
    color: #f0f0f0 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
}

/* Individual dropdown option */
div[role="option"] {
    background-color: transparent !important;
    padding: 10px !important;
    color: #f0f0f0 !important;
    font-size: 14px !important;
}

/* Hover effect for dropdown options */
div[role="option"]:hover {
    background-color: rgba(60, 60, 60, 0.7) !important;
}

/* 3-dot top-right menu icon (white) */
[data-testid="stActionMenuButton"] {
    filter: invert(100%) !important;
}

/* Dropdown panel inside 3-dot menu */
[data-testid="stActionMenu"] {
    background-color: rgba(20, 20, 20, 0.95) !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

/* Buttons inside 3-dot menu */
[data-testid="stActionMenu"] button {
    color: white !important;
}

[data-testid="stActionMenu"] button:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
}
/* DARK MODE FOR DROPDOWN OPTIONS PANEL */
div[data-baseweb="popover"] {
    background-color: rgba(20, 20, 20, 0.95) !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.6) !important;
}

div[data-baseweb="menu"] div[role="option"] {
    background-color: transparent !important;
    color: white !important;
}

div[data-baseweb="menu"] div[role="option"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
}

/* DARK MODE FOR STREAMLIT 3-DOT MENU */
[data-testid="stActionMenuButton"] {
    filter: invert(100%) brightness(200%) !important; /* Makes 3-dot icon white */
}

[data-testid="stActionMenu"] {
    background-color: rgba(20, 20, 20, 0.95) !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
}

[data-testid="stActionMenu"] button {
    color: white !important;
    background-color: transparent !important;
}

[data-testid="stActionMenu"] button:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
}


    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="width: 100%; text-align: center; margin: 2rem 0 1rem 0;">
        <h1 style="font-size: 4rem; font-weight: 800; color: white; margin-bottom: 0.5rem;">DATALICIOUS</h1>
        <p style="font-size: 1.2rem; letter-spacing: 2px; color: white;">SLEEK. SMART. STREAMLINED.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    "Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma"
)
st.header("Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        st.subheader("Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.header("Generate Summary")

        summary = None
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.success("Summary Generated!")
        with col2:
            st.markdown("The summary provides a GPT-style overview based on sample data.")

        if summary:
            st.markdown(f"#### Summary Output:\n{summary}")

        st.header("Chart Generator")

        numeric_columns = df.select_dtypes(include=["float64", "int64", "int32"]).columns.tolist()
        if numeric_columns:
            with st.expander("Chart Controls", expanded=True):
                selected_column = st.selectbox("Choose column:", numeric_columns)
                top_n = st.slider("Top N values:", 5, 20, 10)

                fig = plot_top_column(df, selected_column, top_n=top_n)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns found for charts.")

        st.header("Ask About This Dataset")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        mode = st.selectbox("Answer style:", ["Normal", "Explain like I'm 5", "Detailed"])
        user_input = st.text_input("Your question:", placeholder="e.g. Which country starts with C?", key="qna_input")

        if user_input:
            with st.spinner("Thinking like a data analyst..."):
                reply = ask_dataset_question(df, user_input, mode=mode)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("ai", reply))

        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"<div class='chat-user'><strong>You:</strong><br>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-ai'><strong>AI:</strong><br>{msg}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin your Datalicious journey.")



