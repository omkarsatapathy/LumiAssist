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
    .main-title {
        text-align: center;
        padding: 1rem 0 0.8rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(31, 38, 135, 0.25);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .main-title h1 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
    }
    .main-title .subtitle {
        font-size: 0.8rem;
        opacity: 0.75;
        margin-top: 0.2rem;
    }
    .lumi-icon-main {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin: 0 auto 0.5rem auto;
        display: block;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        background: rgba(90, 90, 192, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    .chat-message {
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 15px;
        color: #e8e8e8;
        font-size: 16px;
        line-height: 1.5;
        max-width: 70%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #5A5AC0 0%, #4A4AAF 100%);
        border-left: 4px solid #4caf50;
        margin-left: auto;
        margin-right: 2rem;
        text-align: right;
    }
    .bot-message {
        background: linear-gradient(135deg, #3a4854 0%, #2d3748 100%);
        border-left: 4px solid #26a69a;
        margin-left: 2rem;
        margin-right: auto;
        text-align: left;
    }
    .user-message-new {
        background: linear-gradient(135deg, #5A5AC0 0%, #4A4AAF 100%);
        border-left: 4px solid #4caf50;
        margin-left: auto;
        margin-right: 2rem;
        text-align: right;
        animation: slideInRight 0.5s ease-out;
    }
    .bot-message-new {
        background: linear-gradient(135deg, #3a4854 0%, #2d3748 100%);
        border-left: 4px solid #26a69a;
        margin-left: 2rem;
        margin-right: auto;
        text-align: left;
        animation: slideInLeft 0.5s ease-out;
    }
    .sidebar-bot {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .sidebar-bot h2 {
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .icon-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .user-icon {
        float: right;
        margin-left: 20px;
    }
    .bot-icon {
        float: left;
        margin-right: 20px;
    }
    .chat-container {
        animation: fadeInUp 0.8s ease-out;
    }
    .stChatInput > div {
        background: rgba(90, 90, 192, 0.2) !important;
        border-radius: 25px !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
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
    if 'last_message_count' not in st.session_state:
        st.session_state.last_message_count = 0
    
    with st.sidebar:
        if bot_icon:
            st.markdown(f"""
            <div class="sidebar-bot">
                <img src="data:image/png;base64,{bot_icon}" class="icon-img">
                <h2>Lumi AI</h2>
                <p><em>Apple Support Assistant</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-bot">
                <h2>Lumi AI</h2>
                <p><em>Apple Support Assistant</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("New Session", type="primary", use_container_width=True):
            clear_session()
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.session_state.processing_message = False
            st.session_state.pending_message = None
            st.session_state.last_message_count = 0
            st.rerun()
    
    # Beautiful main header
    if bot_icon:
        st.markdown(f"""
        <div class="main-title">
            <img src="data:image/png;base64,{bot_icon}" class="lumi-icon-main">
            <h1>Lumi: The Apple Assistant!</h1>
            <div class="subtitle">Your intelligent support companion for all Apple laptop needs</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-title">
            <h1>🤖 Lumi: The Apple Assistant!</h1>
            <div class="subtitle">Your intelligent support companion for all Apple laptop needs</div>
        </div>
        """, unsafe_allow_html=True)
    
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        current_count = len(st.session_state.messages)
        
        for i, (role, message) in enumerate(st.session_state.messages):
            # Determine if this message should animate (new message)
            # Bot messages should never animate in final chat history (they already animated during streaming)
            is_new_message = i >= st.session_state.last_message_count and role == "user"
            
            if role == "user":
                message_class = "user-message-new" if is_new_message else "user-message"
                if human_icon:
                    st.markdown(f"""
                    <div class="chat-message {message_class}">
                        <img src="data:image/png;base64,{human_icon}" class="icon-img user-icon">
                        <strong>You:</strong><br>
                        <div style="margin-right: 70px; text-align: right;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message {message_class}">
                        <strong>You:</strong><br>
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Bot messages always use non-animated class in final chat history
                if bot_icon:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <img src="data:image/png;base64,{bot_icon}" class="icon-img bot-icon">
                        <strong>Lumi:</strong><br>
                        <div style="margin-left: 70px;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>Lumi:</strong><br>
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Update the last message count after rendering
        st.session_state.last_message_count = current_count
        st.markdown('</div>', unsafe_allow_html=True)
    
    user_input = st.chat_input("Type your message here...")
    
    # Handle new user input
    if user_input and not st.session_state.processing_message:
        # Immediately add user message and set up for processing
        st.session_state.messages.append(("user", user_input))
        st.session_state.pending_message = user_input
        st.session_state.processing_message = True
        st.rerun()
    
    # Process pending message (this runs after rerun when user message is visible)
    if st.session_state.processing_message and st.session_state.pending_message:
        process_bot_response(st.session_state.pending_message)

def process_bot_response(user_message):
    """Process the bot response after user message is displayed"""
    
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
        # Print the HTTP request details
        request_url = "http://localhost:5001/chat"
        request_payload = {
            "message": user_message,
            "session_id": st.session_state.session_id
        }
        
        print("\n" + "="*60)
        print("FRONTEND → API HTTP REQUEST")
        print("="*60)
        print(f"URL: {request_url}")
        print(f"Method: POST")
        print(f"Headers: Content-Type: application/json")
        print(f"Payload: {json.dumps(request_payload, indent=2)}")
        print("="*60)
        
        response = requests.post(
            request_url,
            json=request_payload,
            timeout=30
        )
        
        print(f"RESPONSE STATUS: {response.status_code}")
        print(f"RESPONSE SIZE: {len(response.content)} bytes")
        print("="*60 + "\n")
        
        if response.status_code == 200:
            data = response.json()
            full_response = data.get('response', 'No response received')
            
            for char in full_response:
                response_text += char
                with response_placeholder.container():
                    if bot_icon:
                        st.markdown(f"""
                        <div class="chat-message bot-message-new">
                            <img src="data:image/png;base64,{bot_icon}" class="icon-img bot-icon">
                            <strong>Lumi:</strong><br>
                            <div style="margin-left: 70px;">{response_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message-new">
                            <strong>Lumi:</strong><br>
                            {response_text}
                        </div>
                        """, unsafe_allow_html=True)
                time.sleep(0.01)
            
            st.session_state.messages.append(("assistant", full_response))
        else:
            error_msg = f"Error: {response.status_code}"
            st.session_state.messages.append(("assistant", error_msg))
            
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to AI agent. Please ensure the API is running."
        st.session_state.messages.append(("assistant", error_msg))
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. Please try again."
        st.session_state.messages.append(("assistant", error_msg))
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.session_state.messages.append(("assistant", error_msg))
    
    # Clear processing flags
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