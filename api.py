from flask import Flask, request, jsonify
from agent import lumi_agent
from tools import init_db
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = lumi_agent.process_message(user_message, session_id)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'intent': lumi_agent.analyze_intent(user_message)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'agent': 'Lumi AI Assistant',
        'version': '1.0'
    })

@app.route('/session/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    """Clear session"""
    lumi_agent.clear_session(session_id)
    return jsonify({'message': f'Session {session_id} cleared'})

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Lumi AI Assistant API',
        'endpoints': {
            'chat': 'POST /chat',
            'health': 'GET /health',
            'clear_session': 'POST /session/{id}/clear'
        }
    })

if __name__ == '__main__':
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found!")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        exit(1)
    
    init_db()
    print("API will be available at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)