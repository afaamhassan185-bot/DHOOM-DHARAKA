import os
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'dhoom_dhadaka_super_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 👑 OWNER/ADMIN ACCOUNT SETUP
# आपके पर्सनल Google अकाउंट की ईमेल यहाँ सेट है
ADMIN_EMAIL = "afaampro15156@gmail.com"

# इन-मेमोरी डेटा (Users, Banned Users, Posts, Messages)
USERS = {}        # {email: {"name": name, "channel": channel_name, "picture": pic, "is_banned": False}}
BANNED_USERS = set()
POSTS = []
MESSAGES = [
    {"username": "System", "text": "धूम धड़ाका YouTube Edition में आपका स्वागत है! 🎉"}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def check_ban_and_geo():
    # 1. Geo-restriction Check (Only India)
    country_code = request.headers.get('CF-IPCountry') or request.headers.get('X-AppEngine-Country')
    if country_code and country_code.upper() != 'IN':
        return """
        <div style="background:#0f0f0f; color:#ff0055; text-align:center; padding:50px; font-family:sans-serif; height:100vh;">
            <h1>⛔ Access Restricted</h1>
            <p style="color:#fff; margin-top:15px; font-size:18px;">"धूम धड़ाका" केवल भारत (India) में उपलब्ध है।</p>
        </div>
        """, 403

    # 2. Ban Check
    user_email = session.get('user_email')
    if user_email and user_email in BANNED_USERS:
        return """
        <div style="background:#111; color:#ff3333; text-align:center; padding:50px; font-family:sans-serif; height:100vh;">
            <h1>🚫 आपका अकाउंट बैन कर दिया गया है!</h1>
            <p style="color:#ccc; margin-top:15px;">आप इस प्लेटफ़ॉर्म पर नियम उल्लंघन के कारण बैन हैं। अधिक जानकारी के लिए एडमिन से संपर्क करें।</p>
        </div>
        """, 403

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>धूम धड़ाका - YouTube Edition</title>
    <link rel="manifest" href="/manifest.json">
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

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; }
        body { background: var(--bg-color); color: var(--text-color); transition: background 0.3s, color 0.3s; padding-bottom: 40px; }

        /* Header / Navbar */
        header { background: var(--header-bg); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }
        .logo-box { display: flex; align-items: center; gap: 10px; }
        .logo-box h1 { font-size: 20px; color: var(--accent-color); font-weight: bold; letter-spacing: -0.5px; }
        .theme-btn { background: none; border: 1px solid var(--border-color); color: var(--text-color); padding: 6px 12px; border-radius: 20px; cursor: pointer; font-size: 12px; }

        .user-profile-header { display: flex; align-items: center; gap: 12px; }
        .channel-badge { background: #0073e6; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .admin-badge { background: #ffaa00; color: #000; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }

        /* Layout Grid */
        .main-container { display: flex; flex-wrap: wrap; gap: 20px; max-width: 1400px; margin: 20px auto; padding: 0 15px; }
        .content-area { flex: 3; min-width: 320px; }
        .sidebar { flex: 1; min-width: 280px; }

        /* Upload Section */
        .upload-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; margin-bottom: 25px; }
        .upload-card h3 { color: var(--accent-color); margin-bottom: 12px; font-size: 16px; }
        .upload-form { display: flex; flex-direction: column; gap: 10px; }
        .upload-form input, .upload-form select { padding: 10px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-color); color: var(--text-color); }
        .upload-btn { background: var(--accent-color); color: #fff; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; }

        /* Videos Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .card { background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color); display: flex; flex-direction: column; }
        .card media, .card video, .card img { width: 100%; height: 180px; object-fit: cover; background: #000; }
        .card-body { padding: 12px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .card-title { font-size: 15px; font-weight: bold; line-height: 1.3; margin-bottom: 6px; }
        .card-author { font-size: 12px; color: #888; margin-bottom: 8px; }

        /* Admin Controls */
        .admin-actions { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border-color); display: flex; gap: 8px; }
        .ban-btn { background: #cc0000; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; }
        .delete-btn { background: #444; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; }

        /* Live Chat */
        .chat-box { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; height: 500px; display: flex; flex-direction: column; padding: 15px; }
        .chat-messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; margin-bottom: 10px; }
        .msg { background: var(--bg-color); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); font-size: 13px; }
        .msg-user { font-weight: bold; font-size: 12px; color: var(--accent-color); }
        .chat-input { display: flex; gap: 8px; }
        .chat-input input { flex: 1; padding: 8px 12px; border-radius: 20px; border: 1px solid var(--border-color); background: var(--bg-color); color: var(--text-color); }
        .chat-input button { background: var(--accent-color); color: white; border: none; padding: 8px 15px; border-radius: 20px; cursor: pointer; }

        /* Auth Modal */
        .login-box { background: var(--card-bg); border: 1px solid var(--border-color); padding: 25px; border-radius: 12px; text-align: center; max-width: 400px; margin: 40px auto; }
        .google-btn { background: #4285F4; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 15px; }

        @media (max-width: 768px) {
            .main-container { flex-direction: column; }
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-box">
            <h1>🔴 धूम धड़ाका</h1>
            <button class="theme-btn" onclick="toggleTheme()">🌓 Theme</button>
        </div>

        <div class="user-profile-header">
            {% if session.get('user_email') %}
                <div>
                    <strong>{{ session.get('user_name') }}</strong>
                    <div style="font-size: 11px; color: #888;">{{ session.get('user_channel') }}</div>
                </div>
                {% if session.get('is_admin') %}
                    <span class="admin-badge">👑 OWNER</span>
                {% else %}
                    <span class="channel-badge">CREATOR</span>
                {% endif %}
                <a href="/logout" style="color: red; font-size: 12px; text-decoration: none; margin-left: 10px;">Logout</a>
            {% endif %}
        </div>
    </header>

    {% if not session.get('user_email') %}
    <!-- Google Account Setup / Login Form -->
    <div class="login-box">
        <h2 style="color: var(--accent-color); margin-bottom: 10px;">Google से साइन इन करें</h2>
        <p style="font-size: 13px; color: #777;">अपना नाम और अपना नया YouTube स्टाइल चैनल बनाएँ!</p>
        
        <form action="/login" method="POST" style="margin-top: 20px; display: flex; flex-direction: column; gap: 12px;">
            <input type="email" name="email" placeholder="Google Email ID (उदा: yourname@gmail.com)" required style="padding: 10px; border-radius: 6px; border: 1px solid var(--border-color);">
            <input type="text" name="name" placeholder="आपका नाम (Display Name)" required style="padding: 10px; border-radius: 6px; border: 1px solid var(--border-color);">
            <input type="text" name="channel" placeholder="चैनल का नाम (उदा: @MyVlogChannel)" required style="padding: 10px; border-radius: 6px; border: 1px solid var(--border-color);">
            <button type="submit" class="google-btn">🌐 Continue to Platform</button>
        </form>
    </div>
    {% else %}

    <div class="main-container">
        <!-- Main Videos & Post Feed -->
        <div class="content-area">
            
            <!-- Channel Upload Form -->
            <div class="upload-card">
                <h3>📹 अपने चैनल पर वीडियो/फोटो अपलोड करें</h3>
                <form class="upload-form" action="/add-post" method="POST" enctype="multipart/form-data">
                    <input type="text" name="title" placeholder="वीडियो या फोटो का टाइटल लिखें..." required>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <input type="file" name="media_file" accept="video/*,image/*" required style="flex: 2;">
                        <select name="type" style="flex: 1;">
                            <option value="video">🎥 Full Video</option>
                            <option value="short">⚡ Short Video</option>
                            <option value="photo">🖼️ Photo Post</option>
                        </select>
                    </div>
                    <button type="submit" class="upload-btn">Publish Post</button>
                </form>
            </div>

            <!-- Feed Section -->
            <h2 style="font-size: 18px; margin-bottom: 15px; color: var(--accent-color);">🔥 Latest Videos & Content</h2>
            <div class="grid">
                {% if posts | length == 0 %}
                    <p style="color: #777; font-style: italic;">अभी कोई पोस्ट अपलोड नहीं की गई है।</p>
                {% else %}
                    {% for item in posts %}
                    <div class="card">
                        {% if item.type == 'photo' %}
                            <img src="/uploads/{{ item.filename }}" alt="Post Image">
                        {% else %}
                            <video controls src="/uploads/{{ item.filename }}"></video>
                        {% endif %}
                        <div class="card-body">
                            <div>
                                <div class="card-title">{{ item.title }}</div>
                                <div class="card-author">👤 {{ item.author_name }} ({{ item.author_channel }})</div>
                            </div>

                            <!-- 👑 ADMIN CONTROLS (केवल आपके अकाउंट को दिखेगा) -->
                            {% if session.get('is_admin') %}
                            <div class="admin-actions">
                                <a href="/delete-post/{{ item.id }}" class="delete-btn">🗑️ Delete</a>
                                {% if item.author_email != session.get('user_email') %}
                                <a href="/ban-user?email={{ item.author_email }}" class="ban-btn" onclick="return confirm('क्या आप इस यूज़र को बैन करना चाहते हैं?');">⛔ Ban User</a>
                                {% endif %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>

        <!-- Right Side Live Chat & Admin Panel -->
        <div class="sidebar">
            <div class="chat-box">
                <h3 style="font-size: 16px; margin-bottom: 10px; color: var(--accent-color);">💬 Live Community Chat</h3>
                <div class="chat-messages" id="chatWindow">
                    {% for msg in messages %}
                    <div class="msg">
                        <div class="msg-user">{{ msg.username }}</div>
                        <div>{{ msg.text }}</div>
                    </div>
                    {% endfor %}
                </div>
                <form class="chat-input" action="/send-message" method="POST">
                    <input type="text" name="text" placeholder="मैसेज भेजें..." required>
                    <button type="submit">Send</button>
                </form>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        // Automatic Day / Night Theme Selector
        function autoTheme() {
            const hour = new Date().getHours();
            // रात 7 बजे से सुबह 6 बजे तक डार्क मोड, बाकी समय लाइट मोड
            if (hour >= 19 || hour < 6) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
            }
        }

        function toggleTheme() {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
        }

        // Run theme setup on load
        autoTheme();

        // Scroll chat to bottom
        let chatWindow = document.getElementById('chatWindow');
        if (chatWindow) { chatWindow.scrollTop = chatWindow.scrollHeight; }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, posts=POSTS, messages=MESSAGES)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email').strip().lower()
    name = request.form.get('name')
    channel = request.form.get('channel')

    session['user_email'] = email
    session['user_name'] = name
    session['user_channel'] = channel

    # 👑 चेक करें कि क्या यह आपका पर्सनल एडमिन अकाउंट है
    session['is_admin'] = (email == ADMIN_EMAIL.lower())

    USERS[email] = {"name": name, "channel": channel}
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add-post', methods=['POST'])
def add_post():
    if not session.get('user_email'):
        return redirect(url_for('home'))

    title = request.form.get('title')
    post_type = request.form.get('type')

    if 'media_file' not in request.files:
        return redirect(url_for('home'))

    file = request.files['media_file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        POSTS.append({
            "id": str(len(POSTS) + 1),
            "title": title,
            "filename": filename,
            "type": post_type,
            "author_email": session.get('user_email'),
            "author_name": session.get('user_name'),
            "author_channel": session.get('user_channel')
        })

    return redirect(url_for('home'))

@app.route('/send-message', methods=['POST'])
def send_message():
    if not session.get('user_email'):
        return redirect(url_for('home'))

    text = request.form.get('text')
    if text:
        MESSAGES.append({
            "username": f"{session.get('user_name')} ({session.get('user_channel')})",
            "text": text
        })
    return redirect(url_for('home'))

# 👑 ADMIN ACTIONS (केवल आपके लिए)
@app.route('/ban-user')
def ban_user():
    if not session.get('is_admin'):
        return "Unauthorized", 403
    
    email_to_ban = request.args.get('email')
    if email_to_ban and email_to_ban != ADMIN_EMAIL:
        BANNED_USERS.add(email_to_ban)
        # बैन किए गए यूज़र की सभी पोस्ट्स को भी हटा दें
        global POSTS
        POSTS = [p for p in POSTS if p['author_email'] != email_to_ban]
        
    return redirect(url_for('home'))

@app.route('/delete-post/<post_id>')
def delete_post(post_id):
    if not session.get('is_admin'):
        return "Unauthorized", 403
    
    global POSTS
    POSTS = [p for p in POSTS if p['id'] != post_id]
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
