import os
import time
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dhoom_dhadaka_ultra_clean_key_2026'

# अपलोड फोल्डर कॉन्फ़िगरेशन
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 👑 OWNER / ADMIN EMAIL ID
ADMIN_EMAIL = "afaampro15156@gmail.com"

# इन-मेमोरी डेटा स्टोरेज
USERS = {}         # {email: {"name": name, "channel": channel}}
BANNED_EMAILS = set()
POSTS = []
MESSAGES = [
    {"username": "System", "text": "धूम धड़ाका ऐप में आपका स्वागत है! 🎉"}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML / CSS / JavaScript टेंप्लेट
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>धूम धड़ाका - All In One Social Platform</title>
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
        .btn-danger { background: #d9534f; color: white; border: none; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: bold; cursor: pointer; }

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
            {% if session.get('user_email') %}
                <span style="margin-left: 10px; font-size: 14px;">👤 <b>{{ session.get('user_name') }}</b> ({{ session.get('user_channel') }})</span>
                {% if session.get('is_admin') %}<span style="background: gold; color: black; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left:5px;">OWNER</span>{% endif %}
                <a href="/logout" style="color: red; margin-left: 10px; text-decoration: none;">Logout</a>
            {% endif %}
        </div>
    </header>

    {% if not session.get('user_email') %}
    <div class="login-box">
        <h2 style="color: var(--accent-color);">लॉगिन / अकाउंट बनाएं</h2>
        <p style="font-size: 12px; color: #777; margin-top: 5px;">अपना नाम और चैनल बनाकर एंटर करें</p>
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
                            <img src="/get-file/{{ post.filename }}">
                        {% else %}
                            <video controls src="/get-file/{{ post.filename }}"></video>
                        {% endif %}
                        <div class="card-body">
                            <div class="card-title">{{ post.title }}</div>
                            <div class="card-meta">By: {{ post.author_channel }}</div>
                            
                            <!-- 👑 OWNER CONTROL PANEL -->
                            {% if session.get('is_admin') %}
                            <div class="admin-controls">
                                <a href="/delete-post/{{ post.id }}" class="btn-danger">Delete Post</a>
                                {% if post.author_email != session.get('user_email') %}
                                <a href="/ban-user?email={{ post.author_email }}" class="btn-danger" onclick="return confirm('क्या आप इस यूजर को बैन करना चाहते हैं?');">Ban User</a>
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
        // Auto Light & Dark Mode according to time
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

# --- Routes ---

@app.route('/')
def index():
    user_email = session.get('user_email')
    if user_email and user_email in BANNED_EMAILS:
        session.clear()
        return "<h1 style='color:red; text-align:center; margin-top:50px;'>⛔ आप इस प्लेटफॉर्म पर बैन कर दिए गए हैं।</h1>", 403
    
    return render_template_string(HTML_TEMPLATE, posts=POSTS, messages=MESSAGES)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    name = request.form.get('name', '').strip()
    channel = request.form.get('channel_name', '').strip()

    if email in BANNED_EMAILS:
        return "<h1 style='color:red; text-align:center; margin-top:50px;'>⛔ आपका ईमेल बैन है!</h1>", 403

    session['user_email'] = email
    session['user_name'] = name
    session['user_channel'] = channel
    session['is_admin'] = (email == ADMIN_EMAIL.lower())

    USERS[email] = {"name": name, "channel": channel}
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if not session.get('user_email'):
        return redirect(url_for('index'))

    title = request.form.get('title')
    media_type = request.form.get('media_type')
    file = request.files.get('file')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        POSTS.insert(0, {
            "id": str(len(POSTS) + 1),
            "title": title,
            "filename": unique_filename,
            "media_type": media_type,
            "author_email": session.get('user_email'),
            "author_name": session.get('user_name'),
            "author_channel": session.get('user_channel')
        })

    return redirect(url_for('index'))

@app.route('/get-file/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/send-msg', methods=['POST'])
def send_msg():
    if not session.get('user_email'):
        return redirect(url_for('index'))

    text = request.form.get('text')
    if text:
        MESSAGES.append({
            "username": f"{session.get('user_name')} ({session.get('user_channel')})",
            "text": text
        })
    return redirect(url_for('index'))

# 👑 OWNER ONLY: BAN USER
@app.route('/ban-user')
def ban_user():
    if not session.get('is_admin'):
        return "Unauthorized", 403

    email_to_ban = request.args.get('email')
    if email_to_ban and email_to_ban != ADMIN_EMAIL:
        BANNED_EMAILS.add(email_to_ban.lower())
        global POSTS
        POSTS = [p for p in POSTS if p['author_email'] != email_to_ban]

    return redirect(url_for('index'))

# 👑 OWNER ONLY: DELETE POST
@app.route('/delete-post/<post_id>')
def delete_post(post_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403

    global POSTS
    POSTS = [p for p in POSTS if p['id'] != post_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
