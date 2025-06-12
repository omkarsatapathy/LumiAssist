import streamlit as st
import requests
import json
import uuid

# ========================================
# STREAMLIT FRONTEND
# ========================================

def run_streamlit():
    """Main Streamlit application"""
    
    # Page config
    st.set_page_config(
        page_title="Lumi - Apple Support AI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom icons
    def load_icon(icon_name):
        try:
            with open(f"icons/{icon_name}", "rb") as f:
                import base64
                return base64.b64encode(f.read()).decode()
        except:
            return None

    bot_icon = load_icon("bot.png")
    human_icon = load_icon("human.png")
    
    # Custom CSS with dark theme
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 15px;
        color: #e8e8e8;
        font-size: 16px;
        line-height: 1.5;
    }
    .user-message {
        background-color: #3d4f42;
        border-left: 4px solid #4caf50;
        margin-left: 20px;
    }
    .bot-message {
        background-color: #3a4854;
        border-left: 4px solid #26a69a;
        margin-right: 20px;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    # Sidebar - Simplified
    with st.sidebar:
        # Bot Icon and Title
        st.markdown("""
        <div class="sidebar-bot">
            <h2>🤖 Lumi AI</h2>
            <p><em>Apple Support Assistant</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # New Session Button
        if st.button("🔄 New Session", type="primary", use_container_width=True):
            # Clear session on backend
            try:
                requests.post(f"http://localhost:5001/session/{st.session_state.session_id}/clear")
            except:
                pass
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.rerun()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Lumi - Intelligent Apple Support Assistant</h1>
        <p>I can help with technical questions and create support complaints</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display messages with custom styling
        for role, message in st.session_state.messages:
            if role == "user":
                if human_icon:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <img src="data:image/png;base64,{human_icon}" class="icon-img" style="float: left; margin-right: 10px;">
                        <strong>You:</strong><br>
                        <div style="margin-left: 70px;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong><br>
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                if bot_icon:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <img src="data:image/png;base64,{bot_icon}" class="icon-img" style="float: left; margin-right: 10px;">
                        <strong>Lumi:</strong><br>
                        <div style="margin-left: 70px;">{message}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 Lumi:</strong><br>
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here... (include all details for complaints)")
    
    if user_input:
        # Add user message
        st.session_state.messages.append(("user", user_input))
        
        # Get AI response
        with st.spinner("🤖 Lumi is analyzing your message..."):
            response = send_message(user_input)
        
        # Add bot response
        st.session_state.messages.append(("assistant", response))
        st.rerun()
    
    # Instructions
    with st.expander("📖 How to Use Lumi"):
        st.markdown("""
        **Lumi is an intelligent AI that can:**
        
        🔍 **Answer Technical Questions**
        - "How do I check battery health?"
        - "My MacBook runs slow, what should I do?"
        
        📝 **Create Support Complaints**
        - Provide all details in one message: name, phone, email, and issue description
        - Example: "Hi, I'm Sarah Johnson, phone 9876543210, email sarah@email.com. My MacBook Pro screen flickers constantly and sometimes goes black."
        
        📋 **Retrieve Complaint Status**
        - "Show me complaint ABC12345"
        - "Check status of complaint XYZ67890"
        
        **Tips:**
        - Be specific about your issue
        - For complaints, include all your details in one message
        - Lumi thinks before responding - no generic answers!
        """)

def send_message(message: str) -> str:
    """Send message to Flask API"""
    try:
        response = requests.post(
            "http://localhost:5001/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response received')
        else:
            return f"❌ Error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to AI agent. Starting up..."
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========================================
# MAIN APPLICATION LAUNCHER
# ========================================

def main():
    """Main application entry point - only run Streamlit frontend"""
    run_streamlit()

if __name__ == "__main__":
    main()