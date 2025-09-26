# app.py
import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from chatbot.core import FinancialChatbot

CSV_PATH = os.path.join('data', 'financials.csv')
bot = FinancialChatbot(CSV_PATH)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# simple in-memory session store (for demo only)
SESSIONS = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    payload = request.json or {}
    message = payload.get('message', '')
    session_id = payload.get('session_id')
    if not session_id:
        session_id = str(len(SESSIONS) + 1)
    session_obj = SESSIONS.get(session_id, {})
    res = bot.interpret(message, session=session_obj)
    # persist session
    SESSIONS[session_id] = res.get('session', session_obj)
    return jsonify({'session_id': session_id, 'reply': res['text'], 'image': res.get('image')})

# serve static files (Flask does this automatically at /static)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)