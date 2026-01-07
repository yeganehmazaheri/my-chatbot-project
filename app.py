from flask import Flask, request, jsonify, Response, session
from flask_cors import CORS
import os
import logging
from document_database import DocumentDatabase
from document_retriever import DocumentRetriever
from chatbot import DocumentChatbot
import json

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # For session

document_db = DocumentDatabase('answers.txt')
document_retriever = DocumentRetriever(document_db)
API_KEY = os.getenv('ZAI_API_KEY', "c35654cc6502485eb24b3d2b47a0946a.n3eGF4CnOUS8YRKF")

chatbot = DocumentChatbot(API_KEY, document_retriever)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        logging.error("Missing 'message' in request")
        return jsonify({"error": "User message is required"}), 400
    
    user_message = data['message']
    logging.info(f"Received message: {user_message}")
    
    # NEW: Use session for basic memory (e.g., if contact was provided)
    if 'contact_provided' not in session:
        session['contact_provided'] = False

    if data.get('stream', False):
        def generate():
            try:
                for chunk in chatbot.get_streaming_response(user_message, session):
                    if chunk.startswith('Error:'):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        break
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            except Exception as e:
                logging.error(f"Streaming error: {str(e)}")
                yield f"data: {json.dumps({'content': f'Error: {str(e)}'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    response = chatbot.get_response(user_message, session)
    logging.info(f"Response sent: {response[:50]}...")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
