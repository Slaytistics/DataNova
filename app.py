import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from summarizer import summarize_dataset
from visualizer import plot_top_column
from figma_exporter import export_to_figma
from qna import ask_dataset_question

# 🔄 Session State
if "chatbox_open" not in st.session_state:
    st.session_state.chatbox_open = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# 🎨 Page Styling
st.set_page_config(page_title="📊 Datalicious", layout="wide")
background_image_url = "https://i.imgur.com/qo8IZvH.jpeg"
assistant_avatar_url = "https://i.imgur.com/dVHOnO7.jpeg"

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{background_image_url}");
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
}}
.block-container {{
    padding: 2rem 3rem;
    max-width: 900px;
    margin: auto;
    background: transparent !important;
}}
.stButton > button,
.stTextInput,
.stSelectbox,
.stSlider,
.stExpander,
.stDataFrame,
.element-container,
.stPlotlyChart {{
    background-color: transparent !important;
    color: black !important;
    border: none !important;
    box-shadow: none !important;
    padding: 12px;
}}
input, textarea, select {{
    background-color: rgba(255,255,255,0.8) !important;
    color: black !important;
    border: 1px solid #ccc !important;
}}
button {{
    background-color: rgba(240,240,240,0.9) !important;
    color: black !important;
    border: 1px solid #ccc !important;
}}
html, body {{
    color: black !important;
}}
.chat-message-user {{
    background: #DCF8C6;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 6px 0;
}}
.chat-message-ai {{
    background: #EAEAEA;
    padding: 8px 12px;
    border-radius: 15px;
    margin: 6px 0;
}}
.floating-avatar {{
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 85px;
    height: 85px;
    border-radius: 50%;
    background-image: url('{assistant_avatar_url}');
    background-size: cover;
    background-position: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 9999;
    transition: transform 0.2s ease;
}}
.floating-avatar:hover {{
    transform: scale(1.05);
}}
</style>
""", unsafe_allow_html=True)

# 💬 Floating Chat Widget (Like LinkedIn)
def render_floating_chat_widget():
    is_open = st.session_state.chatbox_open
    chat_display = "block" if is_open else "none"
    
    components.html(f"""
    <div id="floating-chat-widget">
        <!-- Floating Avatar Button -->
        <div class="floating-avatar" onclick="toggleChatWidget()" title="Click to chat with AI Assistant">
            <div class="chat-notification">💬</div>
        </div>
        
        <!-- Chat Window -->
        <div id="chatWindow" class="chat-window" style="display: {chat_display};">
            <div class="chat-header">
                <div class="chat-title">
                    <img src="{assistant_avatar_url}" class="chat-avatar-small" alt="AI">
                    <span>AI Data Assistant</span>
                </div>
                <button class="close-chat" onclick="closeChatWidget()">&times;</button>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="ai-message">
                    <img src="{assistant_avatar_url}" class="message-avatar" alt="AI">
                    <div class="message-content">
                        <div class="message-bubble ai-bubble">
                            Hi! I'm your AI data assistant. Upload a dataset and I'll help you analyze it! 📊
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chat-input-area">
                <input type="text" id="chatInput" placeholder="Ask about your dataset..." 
                       onkeypress="handleEnterKey(event)">
                <button onclick="sendMessage()" class="send-button">Send</button>
            </div>
        </div>
    </div>
    
    <style>
        .floating-avatar {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-image: url('{assistant_avatar_url}');
            background-size: cover;
            background-position: center;
            box-shadow: 0px 4px 16px rgba(0,0,0,0.3);
            cursor: pointer;
            z-index: 10000;
            transition: all 0.3s ease;
            border: 3px solid #fff;
        }}
        
        .floating-avatar:hover {{
            transform: scale(1.1);
            box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
        }}
        
        .chat-notification {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .chat-window {{
            position: fixed;
            bottom: 100px;
            right: 25px;
            width: 380px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0px 8px 30px rgba(0,0,0,0.3);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .chat-header {{
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .chat-title {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .chat-avatar-small {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
        }}
        
        .close-chat {{
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
        }}
        
        .ai-message, .user-message {{
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }}
        
        .user-message {{
            justify-content: flex-end;
        }}
        
        .message-avatar {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .message-content {{
            max-width: 70%;
        }}
        
        .message-bubble {{
            padding: 10px 14px;
            border-radius: 18px;
            word-wrap: break-word;
        }}
        
        .ai-bubble {{
            background: #e9ecef;
            color: #333;
        }}
        
        .user-bubble {{
            background: #007bff;
            color: white;
            margin-left: auto;
        }}
        
        .chat-input-area {{
            padding: 15px;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
        }}
        
        #chatInput {{
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }}
        
        .send-button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .send-button:hover {{
            background: #0056b3;
        }}
    </style>
    
    <script>
        let chatOpen = {str(is_open).lower()};
        
        function toggleChatWidget() {{
            chatOpen = !chatOpen;
            const chatWindow = document.getElementById('chatWindow');
            chatWindow.style.display = chatOpen ? 'block' : 'none';
            
            // Notify Streamlit about state change
            window.parent.postMessage({{
                type: 'chat-toggle',
                isOpen: chatOpen
            }}, '*');
        }}
        
        function closeChatWidget() {{
            chatOpen = false;
            document.getElementById('chatWindow').style.display = 'none';
            
            // Notify Streamlit about state change
            window.parent.postMessage({{
                type: 'chat-toggle',
                isOpen: false
            }}, '*');
        }}
        
        function sendMessage() {{
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (message) {{
                // Add user message to chat
                addMessageToChat(message, 'user');
                
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'chat-message',
                    message: message
                }}, '*');
                
                input.value = '';
            }}
        }}
        
        function handleEnterKey(event) {{
            if (event.key === 'Enter') {{
                sendMessage();
            }}
        }}
        
        function addMessageToChat(message, sender) {{
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = sender === 'user' ? 'user-message' : 'ai-message';
            
            if (sender === 'user') {{
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <div class="message-bubble user-bubble">${{message}}</div>
                    </div>
                `;
            }} else {{
                messageDiv.innerHTML = `
                    <img src="{assistant_avatar_url}" class="message-avatar" alt="AI">
                    <div class="message-content">
                        <div class="message-bubble ai-bubble">${{message}}</div>
                    </div>
                `;
            }}
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        // Listen for messages from Streamlit
        window.addEventListener('message', function(event) {{
            if (event.data.type === 'ai-response') {{
                addMessageToChat(event.data.message, 'ai');
            }}
        }});
    </script>
    """, height=0)

# 📊 App Interface
st.title("📊 Datalicious — AI Data Assistant")
st.markdown("Upload structured data, generate insights, visualize trends, and export them professionally. Powered by Together AI + Figma 🎨")
st.divider()
st.header("📁 Step 1: Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # 🧼 Clean dataset
        df = pd.read_csv(uploaded_file)
        df.columns = [col.strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        # 👀 Preview
        st.subheader("👓 Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.divider()
        st.header("📋 Step 2: Generate Summary")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🧠 Generate Summary"):
                with st.spinner("Calling Together AI..."):
                    summary = summarize_dataset(df.head(7))
                    st.session_state["summary"] = summary
                    st.success("✅ Summary Generated!")
        with col2:
            st.markdown("This summary provides a GPT-style interpretation of your dataset.")

        if "summary" in st.session_state:
            st.markdown(f"#### 🔍 Summary Output:\n{st.session_state['summary']}")

        st.divider()
        st.header("📊 Step 3: Chart Generator")

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
        st.header("🎨 Step 4: Export to Figma")
        if "summary" in st.session_state:
            dataset_name = uploaded_file.name.split(".")[0]
            if st.button("🎨 Export Summary to Figma"):
                with st.spinner("Sending to Figma..."):
                    result = export_to_figma(st.session_state["summary"], dataset_name=dataset_name)
                    st.toast("📤 Exported to Figma!")
                    st.success(result)

        # Render floating chat widget when dataset is loaded
        render_floating_chat_widget()

        # Handle chat messages (hidden from main interface)
        if st.session_state.chatbox_open:
            # Process any new messages
            if "pending_question" in st.session_state and st.session_state.pending_question:
                user_question = st.session_state.pending_question
                st.session_state.pending_question = ""
                
                # Get AI response
                with st.spinner("AI is thinking..."):
                    ai_response = ask_dataset_question(df, user_question, mode="Normal")
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("ai", ai_response))
                    
                    # Send response back to chat widget
                    st.components.v1.html(f"""
                    <script>
                        window.parent.postMessage({{
                            type: 'ai-response',
                            message: `{ai_response.replace('`', '\\`').replace('"', '\\"')}`
                        }}, '*');
                    </script>
                    """, height=0)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")

else:
    st.info("⬆️ Upload a CSV file to begin your Datalicious journey.")
