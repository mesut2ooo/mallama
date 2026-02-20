# app.py
import os
import json
import requests
import uuid
from flask import Flask, render_template, request, Response, jsonify, abort
from werkzeug.utils import secure_filename
from datetime import datetime

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
           template_folder=os.path.join(BASE_DIR, 'templates'),
           static_folder=os.path.join(BASE_DIR, 'static'))

# Use user directory for data storage
app.config['UPLOAD_FOLDER'] = os.path.expanduser("~/.mallama/uploads")
app.config['CONVERSATIONS_FOLDER'] = os.path.expanduser("~/.mallama/conversations")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERSATIONS_FOLDER'], exist_ok=True)

OLLAMA_BASE = "http://localhost:11434"

# Helper: build prompt from messages and system
def build_prompt(messages, system_prompt=""):
    prompt = ""
    if system_prompt:
        prompt += f"System: {system_prompt}\n"
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
        else:
            prompt += f"{role}: {content}\n"
    prompt += "Assistant:"
    return prompt

# Route: serve UI
@app.route('/')
def index():
    return render_template('index.html')

# Route: get installed models
@app.route('/models', methods=['GET'])
def get_models():
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags")
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            return jsonify([m['name'] for m in models])
        else:
            return jsonify([])
    except:
        return jsonify([])

# Route: streaming chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    model = data.get('model')
    messages = data.get('messages', [])
    system = data.get('system', '')
    temperature = data.get('temperature', 0.7)
    top_p = data.get('top_p', 0.9)
    max_tokens = data.get('max_tokens', 2048)

    if not model:
        return jsonify({'error': 'Model not specified'}), 400

    # Build prompt from messages
    prompt = build_prompt(messages, system)

    # Prepare payload for Ollama generate
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens
        }
    }

    def generate():
        try:
            with requests.post(f"{OLLAMA_BASE}/api/generate", json=payload, stream=True) as r:
                if r.status_code != 200:
                    yield f"data: ERROR: {r.status_code}\n\n"
                    return
                
                for line in r.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            # Check for thinking tokens
                            if 'thinking' in chunk and chunk['thinking']:
                                try:
                                    yield f"data: {json.dumps({'thinking': chunk['thinking']})}\n\n"
                                except GeneratorExit:
                                    return
                            # Check for response tokens
                            if 'response' in chunk and chunk['response']:
                                try:
                                    yield f"data: {json.dumps({'token': chunk['response']})}\n\n"
                                except GeneratorExit:
                                    return
                            if chunk.get('done', False):
                                try:
                                    yield f"data: [DONE]\n\n"
                                except GeneratorExit:
                                    pass
                                return
                        except:
                             continue
        except Exception as e:
            try:
                yield f"data: ERROR: {str(e)}\n\n"
            except GeneratorExit:
                pass

    response = Response(generate(), mimetype='text/event-stream')
    # Add these headers to prevent caching and handle disconnections
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    return response

# Route: stop generation (client-side abort only)
@app.route('/stop', methods=['POST'])
def stop():
    # Just acknowledge the stop request
    return jsonify({'status': 'stopped'})

# Route: save conversation
@app.route('/save', methods=['POST'])
def save_conversation():
    data = request.json
    if not data:
        return jsonify({'error': 'No data'}), 400

    if 'name' not in data:
        messages = data.get('messages', [])
        first_user_msg = next((m for m in messages if m.get('role') == 'user'), None)
        if first_user_msg:
            content = first_user_msg.get('content', '')
            name = content[:30] + '...' if len(content) > 30 else content
            name = name.replace('\n', ' ').strip()
            data['name'] = name or 'New Chat'
        else:
            data['name'] = 'New Chat'
    
    filename = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
    filepath = os.path.join(app.config['CONVERSATIONS_FOLDER'], filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'filename': filename})

# Route: load conversation
@app.route('/load', methods=['POST'])
def load_conversation():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Filename missing'}), 400
    filepath = os.path.join(app.config['CONVERSATIONS_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    with open(filepath, 'r') as f:
        conversation = json.load(f)
    return jsonify(conversation)

# app.py - Add/modify these functions

@app.route('/conversations', methods=['GET'])
def list_conversations():
    """List conversations with their modification times"""
    files = []
    conv_dir = app.config['CONVERSATIONS_FOLDER']
    
    for f in os.listdir(conv_dir):
        if f.endswith('.json'):
            filepath = os.path.join(conv_dir, f)
            stat = os.stat(filepath)
            files.append({
                'filename': f,
                'modified': stat.st_mtime,  # Last modified timestamp
                'created': stat.st_ctime     # Creation time (or last metadata change)
            })
    
    # Sort by modified time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

# Add new route for renaming conversations
@app.route('/rename', methods=['POST'])
def rename_conversation():
    """Rename a conversation file"""
    data = request.json
    filename = data.get('filename')
    new_name = data.get('new_name')
    
    if not filename or not new_name:
        return jsonify({'error': 'Missing filename or new name'}), 400
    
    filepath = os.path.join(app.config['CONVERSATIONS_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Load the conversation
    with open(filepath, 'r') as f:
        conversation = json.load(f)
    
    # Update the name
    conversation['name'] = new_name.strip() or 'New Chat'
    
    # Save back to the same file
    with open(filepath, 'w') as f:
        json.dump(conversation, f, indent=2)
    
    return jsonify({'status': 'renamed', 'filename': filename})

# Route: upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        return jsonify({'filename': unique_name, 'original': filename})

# Route: delete a single conversation
@app.route('/delete', methods=['POST'])
def delete_conversation():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'Filename missing'}), 400
    
    filepath = os.path.join(app.config['CONVERSATIONS_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'status': 'deleted'})
    return jsonify({'error': 'File not found'}), 404

# Route: delete all conversations
@app.route('/delete-all', methods=['POST'])
def delete_all_conversations():
    try:
        for filename in os.listdir(app.config['CONVERSATIONS_FOLDER']):
            if filename.endswith('.json'):
                filepath = os.path.join(app.config['CONVERSATIONS_FOLDER'], filename)
                os.remove(filepath)
        return jsonify({'status': 'all deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500