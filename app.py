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
    .chat-message {
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 15px;
        color: #e8e8e8;
        font-size: 16px;
        line-height: 1.5;
        max-width: 70%;
    }
    .user-message {
        background-color: #3d4f42;
        border-left: 4px solid #4caf50;
        margin-left: auto;
        margin-right: 2rem;
        text-align: right;
    }
    .bot-message {
        background-color: #3a4854;
        border-left: 4px solid #26a69a;
        margin-left: 2rem;
        margin-right: auto;
        text-align: left;
    }
    .sidebar-bot {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .icon-img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-bottom: 0.5rem;
    }
    .user-icon {
        float: right;
        margin-left: 20px;
    }
    .bot-icon {
        float: left;
        margin-right: 20px;
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
    
    with st.sidebar:
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
            st.rerun()
    
    chat_container = st.container()
    
    with chat_container:
        for role, message in st.session_state.messages:
            if role == "user":
                if human_icon:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <img src="data:image/png;base64,{human_icon}" class="icon-img user-icon">
                        <strong>You:</strong><br>
                        <div style="margin-right: 70px; text-align: right;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong><br>
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
            else:
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
                        <div class="chat-message bot-message">
                            <img src="data:image/png;base64,{bot_icon}" class="icon-img bot-icon">
                            <strong>Lumi:</strong><br>
                            <div style="margin-left: 70px;">{response_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message bot-message">
                            <strong>Lumi:</strong><br>
                            {response_text}
                        </div>
                        """, unsafe_allow_html=True)
                time.sleep(0.02)
            
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