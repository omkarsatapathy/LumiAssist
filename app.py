import streamlit as st
import requests
import json
import uuid
import time

def run_streamlit():
    st.set_page_config(
        page_title="Lumi - Apple Support AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    def load_icon(icon_name):
        try:
            with open(f"icons/{icon_name}", "rb") as f:
                import base64
                return base64.b64encode(f.read()).decode()
        except:
            return None

    bot_icon = load_icon("bot.png")
    human_icon = load_icon("human.png")
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #5A5AC0 0%, #4848A8 50%, #5A5AC0 100%) !important;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px;
        padding: 2rem 2rem 200px 2rem !important; /* Large bottom padding */
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .main-title {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .main-title h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        background: linear-gradient(45deg, #ffffff, #e0e0ff);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-title p {
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    .message-container {
        display: flex;
        align-items: flex-start;
        margin: 2rem 0;
        animation: slideIn 0.3s ease-out;
    }
    
    .user-message-container {
        justify-content: flex-end;
        margin-left: 20%;
    }
    
    .bot-message-container {
        justify-content: flex-start;
        margin-right: 20%;
    }
    
    .message-icon {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    .user-icon {
        margin-left: 15px;
        order: 2;
    }
    
    .bot-icon {
        margin-right: 15px;
        order: 1;
    }
    
    .message-bubble {
        max-width: 70%;
        padding: 1.5rem;
        border-radius: 20px;
        color: white;
        font-size: 16px;
        line-height: 1.6;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%);
        border-bottom-right-radius: 5px;
        order: 1;
    }
    
    .user-bubble::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: -10px;
        width: 0;
        height: 0;
        border: 10px solid transparent;
        border-left-color: rgba(255, 255, 255, 0.2);
        border-bottom: 0;
        border-right: 0;
        margin-top: -5px;
        margin-left: -5px;
    }
    
    .bot-bubble {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.2) 100%);
        border-bottom-left-radius: 5px;
        order: 2;
    }
    
    .bot-bubble::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: -10px;
        width: 0;
        height: 0;
        border: 10px solid transparent;
        border-right-color: rgba(0, 0, 0, 0.25);
        border-bottom: 0;
        border-left: 0;
        margin-top: -5px;
        margin-right: -5px;
    }
    
    .message-label {
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 14px;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .message-content {
        font-weight: 400;
    }
    
    /* Spacer to prevent overlap with input */
    .chat-spacer {
        height: 150px;
        width: 100%;
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-icon {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 0 auto 1rem auto;
        display: block;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border: 4px solid rgba(255, 255, 255, 0.3);
        animation: pulse 2s infinite;
    }
    
    .sidebar-content h2 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .sidebar-content p {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 400;
        font-style: italic;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0.15) 100%) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 15px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.25) 100%) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Fixed input at bottom */
    .input-container {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 800px !important;
        z-index: 1000 !important;
        background: rgba(255, 255, 255, 0.2) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 25px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        padding: 12px 24px !important;
    }
    
    /* Hide default streamlit input styling */
    div[data-testid="stTextInput"] {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 90% !important;
        max-width: 800px !important;
        z-index: 1000 !important;
    }
    
    div[data-testid="stTextInput"] > label {
        display: none !important;
    }
    
    div[data-testid="stTextInput"] > div {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 25px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        padding: 12px 24px !important;
    }
    
    div[data-testid="stTextInput"] > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stTextInput"] input {
        background: transparent !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: none !important;
        padding: 8px 0 !important;
    }
    
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        font-style: italic !important;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }
        50% {
            box-shadow: 0 8px 35px rgba(255, 255, 255, 0.3);
        }
        100% {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if 'processing_message' not in st.session_state:
        st.session_state.processing_message = False
    if 'pending_message' not in st.session_state:
        st.session_state.pending_message = None
    
    with st.sidebar:
        if bot_icon:
            st.markdown(f"""
            <div class="sidebar-content">
                <img src="data:image/png;base64,{bot_icon}" class="sidebar-icon">
                <h2>Lumi</h2>
                <p>Apple Support Assistant</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-content">
                <div style="font-size: 80px; margin-bottom: 1rem;">🤖</div>
                <h2>Lumi</h2>
                <p>Apple Support Assistant</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("New Session", type="primary", use_container_width=True):
            clear_session()
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.session_state.processing_message = False
            st.session_state.pending_message = None
            st.rerun()
    
    # Main title
    if bot_icon:
        st.markdown(f"""
        <div class="main-title">
            <img src="data:image/png;base64,{bot_icon}" style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 1rem; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);">
            <p>Your intelligent support companion for all Apple laptop needs</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-title">
            <div style="font-size: 80px; margin-bottom: 1rem;">🤖</div>
            <h1>Lumi: The Apple Assistant!</h1>
            <p>Your intelligent support companion for all Apple laptop needs</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display messages
    for role, message in st.session_state.messages:
        if role == "user":
            user_icon_html = f'<img src="data:image/png;base64,{human_icon}" class="message-icon user-icon">' if human_icon else '<div class="message-icon user-icon" style="background: linear-gradient(135deg, #ff6b6b, #ff8e8e); display: flex; align-items: center; justify-content: center; font-size: 20px;">👤</div>'
            st.markdown(f"""
            <div class="message-container user-message-container">
                <div class="message-bubble user-bubble">
                    <div class="message-label">You</div>
                    <div class="message-content">{message}</div>
                </div>
                {user_icon_html}
            </div>
            """, unsafe_allow_html=True)
        else:
            bot_icon_html = f'<img src="data:image/png;base64,{bot_icon}" class="message-icon bot-icon">' if bot_icon else '<div class="message-icon bot-icon" style="background: linear-gradient(135deg, #4ecdc4, #44a08d); display: flex; align-items: center; justify-content: center; font-size: 20px;">🤖</div>'
            st.markdown(f"""
            <div class="message-container bot-message-container">
                {bot_icon_html}
                <div class="message-bubble bot-bubble">
                    <div class="message-label">Lumi</div>
                    <div class="message-content">{message}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add spacer to prevent overlap
    st.markdown('<div class="chat-spacer"></div>', unsafe_allow_html=True)
    
    # Auto-scroll to bottom using streamlit's native method
    if len(st.session_state.messages) > 0:
        st.markdown("""
        <script>
        setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    # Input handling
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    
    user_input = st.text_input("", placeholder="Type your message here...", key=f"chat_input_{st.session_state.input_key}")
    
    if user_input and not st.session_state.processing_message:
        st.session_state.messages.append(("user", user_input))
        st.session_state.pending_message = user_input
        st.session_state.processing_message = True
        st.session_state.input_key += 1
        st.rerun()
    
    if st.session_state.processing_message and st.session_state.pending_message:
        process_bot_response(st.session_state.pending_message)

def process_bot_response(user_message):
    def load_icon(icon_name):
        try:
            with open(f"icons/{icon_name}", "rb") as f:
                import base64
                return base64.b64encode(f.read()).decode()
        except:
            return None

    bot_icon = load_icon("bot.png")
    response_placeholder = st.empty()
    response_text = ""
    
    try:
        response = requests.post(
            "http://localhost:5001/chat",
            json={"message": user_message, "session_id": st.session_state.session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            full_response = data.get('response', 'No response received')
            
            # Typing animation
            for char in full_response:
                response_text += char
                bot_icon_html = f'<img src="data:image/png;base64,{bot_icon}" class="message-icon bot-icon">' if bot_icon else '<div class="message-icon bot-icon" style="background: linear-gradient(135deg, #4ecdc4, #44a08d); display: flex; align-items: center; justify-content: center; font-size: 20px;">🤖</div>'
                
                with response_placeholder.container():
                    st.markdown(f"""
                    <div class="message-container bot-message-container">
                        {bot_icon_html}
                        <div class="message-bubble bot-bubble">
                            <div class="message-label">Lumi</div>
                            <div class="message-content">{response_text}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(0.01)
            
            st.session_state.messages.append(("assistant", full_response))
        else:
            st.session_state.messages.append(("assistant", f"Error: {response.status_code}"))
            
    except Exception as e:
        st.session_state.messages.append(("assistant", f"Error: {str(e)}"))
    
    st.session_state.processing_message = False
    st.session_state.pending_message = None
    st.rerun()

def clear_session():
    try:
        requests.post(f"http://localhost:5001/session/{st.session_state.session_id}/clear")
    except:
        pass

def main():
    run_streamlit()

if __name__ == "__main__":
    main()