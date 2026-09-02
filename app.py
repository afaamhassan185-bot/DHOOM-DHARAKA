import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dhoom_dhadaka_no_google_secret_key_9304'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dhoom_dhadaka.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'

# 👑 OWNER/ADMIN EMAIL ID
ADMIN_EMAIL = "afaampro15156@gmail.com"

# --- Database Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    channel_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)  # video, photo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Frontend HTML Template ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>धूम धड़ाका - Official YouTube Style Platform</title>
    <style>
        :root {
            --bg-color: #ffffff;
            --card-bg: #f9f9f9;
            --text-color: #0f0f0f;
            --border-color: #e5e5e5;
            --header-bg: #ffffff;
            --accent-color: #ff0000;
        }
        [data-theme="dark"] {
            --bg-color: #0f0f0f;
            --card-bg: #1f1f1f;
            --text-color: #ffffff;
            --border-color: #333333;
            --header-bg: #121212;
            --accent-color: #ff0055;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: var(--bg-color); color: var(--text-color); transition: 0.3s; padding-bottom: 30px; }

        header { background: var(--header-bg); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }
        .logo { font-size: 22px; color: var(--accent-color); font-weight: bold; text-decoration: none; }
        
        .main-wrapper { display: flex; flex-wrap: wrap; gap: 20px; max-width: 1400px; margin: 20px auto; padding: 0 15px; }
        .content-area { flex: 3; min-width: 300px; }
        .sidebar { flex: 1; min-width: 280px; }

        .upload-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; margin-bottom: 20px; }
        .upload-card input, .upload-card select, .upload-card button { width: 100%; padding: 10px; margin-top: 8px; border-radius: 6px; border: 1px solid var(--border-color); }
        .upload-card button { background: var(--accent-color); color: white; border: none; font-weight: bold; cursor: pointer; }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; overflow: hidden; }
        .card video, .card img { width: 100%; height: 180px; object-fit: cover; background: #000; }
        .card-body { padding: 10px; }
        .card-title { font-weight: bold; margin-bottom: 5px; }
        .card-meta { font-size: 12px; color: #777; }

        .admin-controls { margin-top: 10px; display: flex; gap: 10px; border-top: 1px dashed var(--border-color); padding-top: 5px; }
        .btn-danger { background: #d9534f; color: white; border: none; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 11px; }

        .chat-box { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; height: 500px; display: flex; flex-direction: column; padding: 12px; }
        .chat-messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .chat-msg { background: var(--bg-color); padding: 8px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 13px; }
        .chat-user { font-weight: bold; color: var(--accent-color); font-size: 11px; }

        .login-box { max-width: 400px; margin: 50px auto; padding: 25px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; text-align: center; }
        .login-box input { width: 100%; padding: 10px; margin-top: 10px; border-radius: 6px; border: 1px solid var(--border-color); }
        .login-box button { width: 100%; padding: 10px; margin-top: 15px; background: var(--accent-color); color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }

        @media (max-width: 768px) {
            .main-wrapper { flex-direction: column; }
        }
    </style>
</head>
<body>

    <header>
        <a href="/" class="logo">🔴 धूम धड़ाका</a>
        <div>
            <button onclick="toggleTheme()" style="padding: 5px 10px; border-radius: 15px; cursor: pointer; border: 1px solid var(--border-color); background: var(--card-bg); color: var(--text-color);">🌓 Mode</button>
            {% if current_user.is_authenticated %}
                <span style="margin-left: 10px; font-size: 14px;">👤 <b>{{ current_user.name }}</b> ({{ current_user.channel_name }})</span>
                {% if current_user.is_admin %}<span style="background: gold; color: black; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">OWNER</span>{% endif %}
                <a href="/logout" style="color: red; margin-left: 10px; text-decoration: none;">Logout</a>
            {% endif %}
        </div>
    </header>

    {% if not current_user.is_authenticated %}
    <div class="login-box">
        <h2 style="color: var(--accent-color);">लॉगिन / अकाउंट बनाएं</h2>
        <p style="font-size: 12px; color: #777; margin-top: 5px;">अपना नाम और चैनल बनाएं</p>
        <form action="/login" method="POST">
            <input type="email" name="email" placeholder="Email Address (उदा: test@gmail.com)" required>
            <input type="text" name="name" placeholder="आपका पूरा नाम" required>
            <input type="text" name="channel_name" placeholder="चैनल का नाम (उदा: @MyVlogs)" required>
            <button type="submit">प्रवेश करें (Enter App)</button>
        </form>
    </div>
    {% else %}

    <div class="main-wrapper">
        <div class="content-area">
            
            <div class="upload-card">
                <h3>📹 अपने चैनल पर वीडियो/फोटो अपलोड करें</h3>
                <form action="/upload" method="POST" enctype="multipart/form-data">
                    <input type="text" name="title" placeholder="शीर्षक / डिस्क्रिप्टन लिखें..." required>
                    <input type="file" name="file" accept="video/*,image/*" required>
                    <select name="media_type">
                        <option value="video">🎥 Video</option>
                        <option value="photo">🖼️ Photo</option>
                    </select>
                    <button type="submit">Publish Now</button>
                </form>
            </div>

            <h2>🔥 Recent Feed</h2>
            <div class="grid" style="margin-top: 15px;">
                {% if posts | length == 0 %}
                    <p style="color: #777; font-style: italic;">अभी कोई पोस्ट अपलोड नहीं की गई है।</p>
                {% else %}
                    {% for post in posts %}
                    <div class="card">
                        {% if post.media_type == 'photo' %}
                            <img src="/static/uploads/{{ post.filename }}">
                        {% else %}
                            <video controls src="/static/uploads/{{ post.filename }}"></video>
                        {% endif %}
                        <div class="card-body">
                            <div class="card-title">{{ post.title }}</div>
                            <div class="card-meta">By: {{ post.author.channel_name }}</div>
                            
                            <!-- 👑 OWNER CONTROL PANEL -->
                            {% if current_user.is_admin %}
                            <div class="admin-controls">
                                <a href="/delete/{{ post.id }}" class="btn-danger">Delete Post</a>
                                {% if post.author.email != current_user.email %}
                                <a href="/ban/{{ post.author.id }}" class="btn-danger" onclick="return confirm('क्या आप इस यूजर को बैन करना चाहते हैं?');">Ban User</a>
                                {% endif %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>

        <div class="sidebar">
            <div class="chat-box">
                <h3 style="color: var(--accent-color); margin-bottom: 10px;">💬 Live Chat Room</h3>
                <div class="chat-messages" id="chat">
                    {% for msg in messages %}
                    <div class="chat-msg">
                        <div class="chat-user">{{ msg.username }}</div>
                        <div>{{ msg.text }}</div>
                    </div>
                    {% endfor %}
                </div>
                <form action="/send-msg" method="POST" style="margin-top: 10px; display: flex; gap: 5px;">
                    <input type="text" name="text" placeholder="मैसेज लिखें..." required style="flex: 1; padding: 8px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-color); color: var(--text-color);">
                    <button type="submit" style="background: var(--accent-color); color: white; border: none; padding: 8px 12px; border-radius: 4px; font-weight: bold; cursor: pointer;">Send</button>
                </form>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        // Automatic Day (Light) and Night (Dark) Mode
        function autoTheme() {
            const h = new Date().getHours();
            document.documentElement.setAttribute('data-theme', (h >= 19 || h < 6) ? 'dark' : 'light');
        }
        function toggleTheme() {
            const c = document.documentElement.getAttribute('data-theme');
            document.documentElement.setAttribute('data-theme', c === 'dark' ? 'light' : 'dark');
        }
        autoTheme();
        const chat = document.getElementById('chat');
        if(chat) chat.scrollTop = chat.scrollHeight;
    </script>
</body>
</html>
"""

# --- App Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated and current_user.is_banned:
        logout_user()
        return "<h1 style='color:red; text-align:center; margin-top:50px;'>⛔ आप इस प्लेटफॉर्म पर बैन किए गए हैं।</h1>", 403
    
    posts = Post.query.order_by(Post.created_at.desc()).all()
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return render_template_string(HTML_TEMPLATE, posts=posts, messages=messages)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').strip().lower()
    name = request.form.get('name')
    channel_name = request.form.get('channel_name')

    user = User.query.filter_by(email=email).first()

    if not user:
        is_admin = (email == ADMIN_EMAIL.lower())
        user = User(email=email, name=name, channel_name=channel_name, is_admin=is_admin)
        db.session.add(user)
        db.session.commit()

    if user.is_banned:
        return "<h1 style='color:red; text-align:center; margin-top:50px;'>⛔ आपका अकाउंट बैन है!</h1>", 403

    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    title = request.form.get('title')
    media_type = request.form.get('media_type')
    file = request.files.get('file')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{datetime.now().timestamp()}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        post = Post(title=title, filename=filename, media_type=media_type, author=current_user)
        db.session.add(post)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/send-msg', methods=['POST'])
@login_required
def send_msg():
    text = request.form.get('text')
    if text:
        msg = Message(username=f"{current_user.name} ({current_user.channel_name})", text=text)
        db.session.add(msg)
        db.session.commit()
    return redirect(url_for('index'))

# 👑 OWNER/ADMIN ONLY: BAN USER
@app.route('/ban/<int:user_id>')
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        user.is_banned = True
        Post.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    return redirect(url_for('index'))

# 👑 OWNER/ADMIN ONLY: DELETE POST
@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        return "Unauthorized", 403

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
