import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# अपलोड फ़ाइलों को स्टोर करने के लिए फोल्डर
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# डेटा मेमोरी में स्टोर करने के लिए (Posts & Messages)
POSTS = []
MESSAGES = [
    {"username": "Admin", "text": "धूम धड़ाका ऐप में आपका स्वागत है! 🎉"}
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def restrict_to_india():
    country_code = request.headers.get('CF-IPCountry') or request.headers.get('X-AppEngine-Country')
    if country_code and country_code.upper() != 'IN':
        return """
        <div style="background:#0f0f0f; color:#ff0055; text-align:center; padding:50px; font-family:sans-serif; height:100vh;">
            <h1>⛔ Access Restricted</h1>
            <p style="color:#fff; margin-top:15px; font-size:18px;">
                "धूम धड़ाका" केवल भारत (India) में उपलब्ध है।
            </p>
        </div>
        """, 403

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>धूम धड़ाका - All-In-One Social Platform</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#ff0055">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0f0f; color: #fff; padding-bottom: 30px; }
        
        header { background: #1f1f1f; padding: 15px; text-align: center; border-bottom: 2px solid #ff0055; position: sticky; top: 0; z-index: 100; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        header h1 { color: #ff0055; font-size: clamp(20px, 4vw, 32px); text-transform: uppercase; letter-spacing: 1px; }
        header p { color: #aaa; font-size: 12px; margin-top: 4px; }
        
        .offline-bar { background: #ffaa00; color: #000; text-align: center; padding: 10px; font-weight: bold; font-size: 14px; display: none; align-items: center; justify-content: center; gap: 15px; }
        .offline-bar button { background: #000; color: #fff; border: none; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; }

        .game-container { display: none; max-width: 900px; margin: 20px auto; background: #1a1a1a; padding: 15px; border-radius: 8px; border: 2px solid #ffaa00; text-align: center; }
        .game-container iframe { width: 100%; height: 450px; border: none; border-radius: 6px; }

        .main-wrapper { display: flex; flex-wrap: wrap; gap: 20px; max-width: 1200px; margin: 20px auto; padding: 0 15px; }
        
        /* Left/Top Content Area */
        .content-area { flex: 2; min-width: 300px; }
        
        /* Right/Bottom Chat Area */
        .chat-area { flex: 1; min-width: 280px; background: #181818; border-radius: 10px; border: 1px solid #333; padding: 15px; height: 600px; display: flex; flex-direction: column; position: sticky; top: 90px; }

        /* Upload Section */
        .upload-section { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px dashed #ff0055; margin-bottom: 20px; }
        .upload-section h3 { color: #ff0055; margin-bottom: 15px; font-size: 18px; display: flex; align-items: center; gap: 8px; }
        .upload-form { display: flex; flex-direction: column; gap: 12px; }
        .form-group { display: flex; gap: 10px; flex-wrap: wrap; }
        .upload-form input, .upload-form select { padding: 10px; background: #2b2b2b; border: 1px solid #444; color: #fff; border-radius: 6px; flex: 1; min-width: 140px; }
        .upload-form button { background: #ff0055; color: #fff; border: none; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; font-size: 15px; }
        .upload-form button:hover { background: #e0004c; }

        .search-bar { margin-bottom: 20px; }
        .search-bar input { width: 100%; padding: 12px 18px; border-radius: 25px; border: 1px solid #333; background: #222; color: #fff; outline: none; font-size: 15px; }
        
        .section-title { font-size: 20px; margin: 20px 0 15px; color: #ff0055; border-left: 4px solid #ff0055; padding-left: 10px; }
        
        /* Grid Layout for Posts */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 15px; }
        .card { background: #1e1e1e; border-radius: 10px; overflow: hidden; position: relative; border: 1px solid #2a2a2a; transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); }
        .card video, .card img { width: 100%; height: 200px; object-fit: cover; background: #000; }
        .card-info { padding: 12px; }
        .card-title { font-size: 15px; font-weight: bold; margin-bottom: 5px; }
        .card-meta { font-size: 12px; color: #888; }
        .empty-msg { color: #666; font-style: italic; padding: 15px 0; }
        
        /* Pro Badges */
        .pro-badge { position: absolute; top: 10px; right: 10px; background: #ff9900; color: #000; font-size: 10px; font-weight: bold; padding: 4px 8px; border-radius: 4px; z-index: 10; }
        .pro-lock { background: rgba(0,0,0,0.85); position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 15px; z-index: 5; }
        .pro-lock button { background: #ff0055; color: white; border: none; padding: 8px 16px; border-radius: 20px; margin-top: 10px; cursor: pointer; font-weight: bold; }

        /* Live Chat Styling */
        .chat-header { color: #ff0055; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px; font-size: 16px; font-weight: bold; }
        .chat-box { flex: 1; overflow-y: auto; padding-right: 5px; display: flex; flex-direction: column; gap: 10px; }
        .chat-msg { background: #262626; padding: 8px 12px; border-radius: 8px; font-size: 13px; line-height: 1.4; }
        .chat-user { color: #ffaa00; font-weight: bold; margin-bottom: 2px; font-size: 12px; }
        .chat-form { display: flex; gap: 8px; margin-top: 10px; }
        .chat-form input { flex: 1; padding: 8px 12px; background: #2b2b2b; border: 1px solid #444; color: #fff; border-radius: 20px; font-size: 13px; outline: none; }
        .chat-form button { background: #ff0055; color: white; border: none; padding: 8px 14px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 12px; }

        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #222; padding: 25px; border-radius: 12px; max-width: 350px; width: 90%; text-align: center; border: 1px solid #ff0055; }
        .upi-btn { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 15px; font-weight: bold; width: 100%; }
        .close-btn { background: #444; color: white; border: none; padding: 6px 12px; border-radius: 4px; margin-top: 10px; cursor: pointer; }

        /* Responsive Breakpoints */
        @media (max-width: 768px) {
            .main-wrapper { flex-direction: column; }
            .chat-area { position: static; height: 350px; }
            .card video, .card img { height: 180px; }
        }
    </style>
</head>
<body>

    <div id="offlineBar" class="offline-bar">
        <span>⚠️ आप ऑफ़लाइन हैं! बोर मत होइए, गेम खेलिए:</span>
        <button onclick="toggleGame()">🎮 Play Sprunki Game</button>
    </div>

    <header>
        <h1>💥 धूम धड़ाका 💥</h1>
        <p>Official Platform for SYED BROTHER VLOG (@afaampro15156)</p>
    </header>

    <div id="gameSection" class="game-container">
        <h3 style="color:#ffaa00; margin-bottom:10px;">🎶 Sprunki Offline Game</h3>
        <iframe src="https://sprunki.org/game-frame" id="sprunkiFrame"></iframe>
    </div>

    <div class="main-wrapper">
        <!-- Content Column (Uploads & Posts) -->
        <div class="content-area">
            
            <div class="upload-section">
                <h3>📤 पोस्ट / फोटो / वीडियो अपलोड करें</h3>
                <form class="upload-form" action="/add-post" method="POST" enctype="multipart/form-data">
                    <input type="text" name="title" placeholder="शीर्षक / डिस्क्रिप्टन लिखें (Title)" required>
                    
                    <div class="form-group">
                        <input type="file" name="media_file" accept="video/*,image/*" required>
                        <select name="type">
                            <option value="video">🎥 Full Video</option>
                            <option value="short">⚡ Short Video</option>
                            <option value="photo">🖼️ Photo Post</option>
                        </select>
                        <select name="is_pro">
                            <option value="false">Free Access</option>
                            <option value="true">Pro Access (₹29)</option>
                        </select>
                    </div>
                    <button type="submit">Upload & Publish</button>
                </form>
            </div>

            <div class="search-bar">
                <input type="text" id="searchInput" onkeyup="filterPosts()" placeholder="फोटो या वीडियो खोजें...">
            </div>

            <!-- Photos & Videos Grid -->
            <div class="section-title">🎬 Videos & Shorts</div>
            <div class="grid" id="videoGrid">
                {% set media_posts = posts | selectattr("type", "ne", "photo") | list %}
                {% if media_posts | length == 0 %}
                    <p class="empty-msg">अभी कोई वीडियो अपलोड नहीं हुआ है।</p>
                {% else %}
                    {% for item in media_posts %}
                    <div class="card post-item" data-title="{{ item.title | lower }}">
                        {% if item.is_pro %}
                            <span class="pro-badge">PRO</span>
                            <div class="pro-lock">
                                <p>🔒 Pro एक्सक्लूसिव</p>
                                <button onclick="openModal()">₹29 में Unlock करें</button>
                            </div>
                        {% else %}
                            <video controls src="/uploads/{{ item.filename }}"></video>
                        {% endif %}
                        <div class="card-info">
                            <div class="card-title">{{ item.title }}</div>
                            <div class="card-meta">{{ item.type | upper }}</div>
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>

            <div class="section-title">🖼️ Photos & Images</div>
            <div class="grid" id="photoGrid">
                {% set photos = posts | selectattr("type", "equalto", "photo") | list %}
                {% if photos | length == 0 %}
                    <p class="empty-msg">अभी कोई फोटो अपलोड नहीं हुई है।</p>
                {% else %}
                    {% for item in photos %}
                    <div class="card post-item" data-title="{{ item.title | lower }}">
                        {% if item.is_pro %}
                            <span class="pro-badge">PRO</span>
                            <div class="pro-lock">
                                <p>🔒 Pro Photo</p>
                                <button onclick="openModal()">Unlock करें</button>
                            </div>
                        {% else %}
                            <img src="/uploads/{{ item.filename }}" alt="Photo">
                        {% endif %}
                        <div class="card-info">
                            <div class="card-title">{{ item.title }}</div>
                            <div class="card-meta">PHOTO</div>
                        </div>
                    </div>
                    {% endfor %}
                {% endif %}
            </div>

        </div>

        <!-- Chat Column -->
        <div class="chat-area">
            <div class="chat-header">💬 Live Chat Box</div>
            <div class="chat-box" id="chatBox">
                {% for msg in messages %}
                <div class="chat-msg">
                    <div class="chat-user">{{ msg.username }}</div>
                    <div>{{ msg.text }}</div>
                </div>
                {% endfor %}
            </div>
            <form class="chat-form" action="/send-message" method="POST">
                <input type="text" name="user" placeholder="नाम..." style="width: 70px; flex: none;" required>
                <input type="text" name="text" placeholder="मैसेज लिखें..." required>
                <button type="submit">भेजें</button>
            </form>
        </div>
    </div>

    <!-- Pro Payment Modal -->
    <div class="modal" id="proModal">
        <div class="modal-content">
            <h3>🔥 धूम धड़ाका PRO 💥</h3>
            <p style="margin-top: 10px; font-size: 14px; color: #ccc;">SYED BROTHER VLOG के एक्सक्लूसिव कंटेंट के लिए ₹29 पे करें।</p>
            <p style="margin-top: 10px; font-size: 16px; font-weight: bold; color: #28a745;">UPI ID: 9304040043@upi</p>
            <a href="upi://pay?pa=9304040043@upi&pn=DhoomDhadaka&am=29&cu=INR" class="upi-btn">Pay ₹29 Now</a>
            <br>
            <button class="close-btn" onclick="closeModal()">बंद करें</button>
        </div>
    </div>

    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW Error:', err));
            });
        }

        window.addEventListener('online', () => {
            document.getElementById('offlineBar').style.display = 'none';
            document.getElementById('gameSection').style.display = 'none';
        });
        
        window.addEventListener('offline', () => {
            document.getElementById('offlineBar').style.display = 'flex';
        });

        function toggleGame() {
            let game = document.getElementById('gameSection');
            game.style.display = game.style.display === 'block' ? 'none' : 'block';
        }

        function filterPosts() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let items = document.getElementsByClassName('post-item');
            for (let item of items) {
                let title = item.getAttribute('data-title');
                item.style.display = title.includes(input) ? "block" : "none";
            }
        }

        function openModal() { document.getElementById('proModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('proModal').style.display = 'none'; }
        
        // Auto scroll chat to bottom
        let chatBox = document.getElementById('chatBox');
        chatBox.scrollTop = chatBox.scrollHeight;
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, posts=POSTS, messages=MESSAGES)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/sw.js')
def service_worker():
    sw_code = """
    const CACHE_NAME = 'dhoom-dhadaka-v4';
    self.addEventListener('install', (e) => {
        e.waitUntil(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.addAll(['/', 'https://sprunki.org/game-frame']);
            })
        );
    });
    self.addEventListener('fetch', (e) => {
        e.respondWith(
            caches.match(e.request).then((res) => {
                return res || fetch(e.request);
            })
        );
    });
    """
    return sw_code, 200, {'Content-Type': 'application/javascript'}

@app.route('/add-post', methods=['POST'])
def add_post():
    title = request.form.get('title')
    post_type = request.form.get('type')
    is_pro = request.form.get('is_pro') == 'true'

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
            "is_pro": is_pro
        })

    return redirect(url_for('home'))

@app.route('/send-message', methods=['POST'])
def send_message():
    username = request.form.get('user')
    text = request.form.get('text')
    if username and text:
        MESSAGES.append({"username": username, "text": text})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
