from flask import Flask, request, jsonify, Response
from agent import lumi_agent
from tools import init_db
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        print(f"\n[API] Received message: {user_message}")
        print(f"[API] Session ID: {session_id}")
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        print("[API] Processing with agent...")
        response = lumi_agent.process_message(user_message, session_id)
        print(f"[API] Agent response ready, sending back to frontend")
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"[API] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-stream', methods=['POST'])
def chat_stream():
    def generate():
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            session_id = data.get('session_id', 'default')
            
            if not user_message:
                yield f"data: {json.dumps({'error': 'Message is required'})}\n\n"
                return
            
            response = lumi_agent.process_message(user_message, session_id)
            
            for char in response:
                yield f"data: {json.dumps({'chunk': char})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'agent': 'Lumi AI Assistant',
        'version': '2.0'
    })

@app.route('/session/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    lumi_agent.clear_session(session_id)
    return jsonify({'message': f'Session {session_id} cleared'})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Lumi AI Assistant API',
        'endpoints': {
            'chat': 'POST /chat',
            'chat_stream': 'POST /chat-stream',
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
    print("API available at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)