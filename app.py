from flask import Flask, render_template, request, jsonify, url_for, session
from uuid import uuid4
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Use a secure, random key

#sqllite 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Config for avatar uploads ---
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#chatbot db model 

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64))
    role = db.Column(db.String(10))  # "user" or "assistant"
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- Journal entries storage ---
ENTRIES_FILE = 'entries.json'

def load_entries():
    if os.path.exists(ENTRIES_FILE):
        with open(ENTRIES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_entries(entries):
    with open(ENTRIES_FILE, 'w') as f:
        json.dump(entries, f, indent=2)

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/journal')
def journal_page():
    return render_template('journal.html')

@app.route('/entries', methods=['GET'])
def get_entries():
    return jsonify({'entries': load_entries()})

@app.route('/add', methods=['POST'])
def add_entry():
    data = request.get_json()
    if not data or 'text' not in data or not data['text'].strip():
        return jsonify({'error': 'Text is required'}), 400
    new_entry = {
        'id': str(uuid4()),
        'text': data['text'],
        'timestamp': datetime.utcnow().isoformat()
    }
    entries = load_entries()
    entries.append(new_entry)
    save_entries(entries)
    return jsonify({'entry': new_entry})

@app.route('/delete/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entries = load_entries()
    entries = [entry for entry in entries if entry['id'] != entry_id]
    save_entries(entries)
    return '', 204
#profile routes
@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    concerns_list = [
        "Anger", "Anxiety and Panic Attacks", "Depression", "Eating disorders",
        "Self-esteem", "Self-harm", "Stress", "Sleep disorders"
    ]
    data = {}

    if request.method == 'POST':
        data['fullname'] = request.form.get('fullname', '')
        data['email'] = request.form.get('email', '')
        data['gender'] = request.form.get('gender', '')
        data['phone'] = request.form.get('phone', '')
        data['age'] = request.form.get('age', '')
        data['concerns'] = request.form.getlist('concerns')

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                data['avatar_url'] = url_for('static', filename=f'uploads/{filename}')
                session['avatar_url'] = data['avatar_url']
            else:
                data['avatar_url'] = None
        else:
            data['avatar_url'] = None
    else:
        data['avatar_url'] = None

    return render_template('profile.html', data=data, concerns=concerns_list)

#kinesiotherapy routes
@app.route('/kinesiotherapy')
def kinesiotherapy():
    base_path = os.path.join(app.static_folder, 'uploads/kinesiotherapy')
    folders = {}

    if os.path.exists(base_path):
        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                images = [
                    f'/static/uploads/kinesiotherapy/{folder}/{img}'
                    for img in os.listdir(folder_path)
                    if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
                ]
                folders[folder] = images

    return render_template('kinesiotherapy.html', folders=folders)
#games routes
@app.route('/games')
def games():
    return render_template("games.html")

#login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "secret":
            return "Login successful!"
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

#signup routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        print(f"New user: {fullname} ({username})")
        return "Signup successful!"
    return render_template('signup.html')

#chatbot routes

client = OpenAI(api_key="#")
@app.route('/chatbot')
def chatbot():
    avatar_url = session.get('avatar_url', 'https://i.ibb.co/d5b84Xw/Untitled-design.png')  # fallback
    return render_template('chatbot.html', avatar_url=avatar_url)

@app.route('/chatbot/get', methods=['POST'])
def get_bot_response():
    user_input = request.json.get("message", "")
    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        session["session_id"] = session_id

    # Store user's message
    db.session.add(ChatMessage(session_id=session_id, role='user', content=user_input))
    db.session.commit()

    # Load conversation history
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
    history = [{"role": m.role, "content": m.content} for m in messages]

    # Generate assistant reply
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are Sage, an empathetic virtual therapist."}] + history,
            temperature=0.7,
            max_tokens=300
        )
        reply = response.choices[0].message.content

        # Store assistant's reply
        db.session.add(ChatMessage(session_id=session_id, role='assistant', content=reply))
        db.session.commit()

        return jsonify({"response": reply})
    except Exception as e:
        print(e)
        return jsonify({"response": "Sorry, I’m having trouble processing that right now."})

if __name__ == '__main__':
    app.run(debug=True)
