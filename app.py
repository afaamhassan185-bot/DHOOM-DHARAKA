import os
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# अपलोड फ़ाइलों को स्टोर करने के लिए फोल्डर
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

VIDEOS = []

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
    <title>धूम धड़ाका - SYED BROTHER VLOG</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#ff0055">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
        body { background: #0f0f0f; color: #fff; padding-bottom: 30px; }
        header { background: #1f1f1f; padding: 15px; text-align: center; border-bottom: 2px solid #ff0055; position: sticky; top: 0; z-index: 100; }
        header h1 { color: #ff0055; font-size: 24px; text-transform: uppercase; letter-spacing: 1px; }
        header p { color: #aaa; font-size: 12px; margin-top: 4px; }
        
        .offline-bar { background: #ffaa00; color: #000; text-align: center; padding: 10px; font-weight: bold; font-size: 14px; display: none; align-items: center; justify-content: center; gap: 15px; }
        .offline-bar button { background: #000; color: #fff; border: none; padding: 5px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; }

        .game-container { display: none; max-width: 800px; margin: 20px auto; background: #1a1a1a; padding: 15px; border-radius: 8px; border: 2px solid #ffaa00; text-align: center; }
        .game-container iframe { width: 100%; height: 450px; border: none; border-radius: 6px; }

        .upload-section { max-width: 800px; margin: 20px auto; background: #1a1a1a; padding: 15px; border-radius: 8px; border: 1px dashed #ff0055; }
        .upload-section h3 { color: #ff0055; margin-bottom: 10px; font-size: 16px; }
        .upload-form { display: flex; flex-wrap: wrap; gap: 10px; }
        .upload-form input, .upload-form select { padding: 8px 12px; background: #2b2b2b; border: 1px solid #444; color: #fff; border-radius: 4px; flex: 1; min-width: 150px; }
        .upload-form button { background: #ff0055; color: #fff; border: none; padding: 10px 18px; border-radius: 4px; font-weight: bold; cursor: pointer; }

        .search-bar { padding: 10px 15px; max-width: 800px; margin: 0 auto; }
        .search-bar input { width: 100%; padding: 10px 15px; border-radius: 20px; border: 1px solid #333; background: #222; color: #fff; outline: none; }
        
        .container { max-width: 800px; margin: 0 auto; padding: 10px; }
        .section-title { font-size: 18px; margin: 20px 0 10px; color: #ff0055; border-left: 4px solid #ff0055; padding-left: 8px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        .card { background: #1e1e1e; border-radius: 10px; overflow: hidden; position: relative; border: 1px solid #2a2a2a; }
        .card video { width: 100%; height: 200px; border: none; background: #000; }
        .card-info { padding: 12px; }
        .card-title { font-size: 14px; font-weight: bold; }
        .empty-msg { color: #666; font-style: italic; padding: 15px 0; }
        
        .pro-badge { position: absolute; top: 10px; right: 10px; background: #ff9900; color: #000; font-size: 10px; font-weight: bold; padding: 4px 8px; border-radius: 4px; z-index: 10; }
        .pro-lock { background: rgba(0,0,0,0.85); position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 15px; z-index: 5; }
        .pro-lock button { background: #ff0055; color: white; border: none; padding: 8px 16px; border-radius: 20px; margin-top: 10px; cursor: pointer; font-weight: bold; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #222; padding: 25px; border-radius: 12px; max-width: 350px; width: 90%; text-align: center; border: 1px solid #ff0055; }
        .upi-btn { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 15px; font-weight: bold; width: 100%; }
        .close-btn { background: #444; color: white; border: none; padding: 6px 12px; border-radius: 4px; margin-top: 10px; cursor: pointer; }
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
        <h3 style="color:#ffaa00; margin-bottom:10px;">🎶 Sprunki Offline Music Game</h3>
        <iframe src="https://sprunki.org/game-frame" id="sprunkiFrame"></iframe>
    </div>

    <div class="upload-section">
        <h3>📁 गैलरी / फाइल एक्सप्लोरर से MP4 वीडियो चुनें</h3>
        <form class="upload-form" action="/add-video" method="POST" enctype="multipart/form-data">
            <input type="text" name="title" placeholder="वीडियो का शीर्षक (Title)" required>
            
            <!-- यहाँ गैलरी / File Explorer डायरेक्ट खुलेगा -->
            <input type="file" name="video_file" accept="video/mp4,video/x-m4v,video/*" required>
            
            <select name="type">
                <option value="video">Full Length Video</option>
                <option value="short">Short Video</option>
            </select>
            <select name="is_pro">
                <option value="false">Free Access</option>
                <option value="true">Pro Access (₹29)</option>
            </select>
            <button type="submit">Upload & Publish</button>
        </form>
    </div>

    <div class="search-bar">
        <input type="text" id="searchInput" onkeyup="filterVideos()" placeholder="वीडियो खोजें...">
    </div>

    <div class="container">
        <div class="section-title">🎬 Full Length Videos</div>
        <div class="grid" id="videoGrid">
            {% set full_videos = videos | selectattr("type", "equalto", "video") | list %}
            {% if full_videos | length == 0 %}
                <p class="empty-msg">अभी कोई फुल वीडियो अपलोड नहीं हुआ है।</p>
            {% else %}
                {% for item in full_videos %}
                <div class="card video-item" data-title="{{ item.title | lower }}">
                    {% if item.is_pro %}
                        <span class="pro-badge">PRO</span>
                        <div class="pro-lock">
                            <p>🔒 Pro एक्सक्लूसिव वीडियो</p>
                            <button onclick="openModal()">₹29 में Unlock करें</button>
                        </div>
                    {% else %}
                        <video controls src="/uploads/{{ item.filename }}"></video>
                    {% endif %}
                    <div class="card-info">
                        <div class="card-title">{{ item.title }}</div>
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        </div>

        <div class="section-title">📱 Shorts</div>
        <div class="grid" id="shortsGrid">
            {% set shorts = videos | selectattr("type", "equalto", "short") | list %}
            {% if shorts | length == 0 %}
                <p class="empty-msg">अभी कोई शॉट अपलोड नहीं हुआ है।</p>
            {% else %}
                {% for item in shorts %}
                <div class="card video-item" data-title="{{ item.title | lower }}">
                    {% if item.is_pro %}
                        <span class="pro-badge">PRO</span>
                        <div class="pro-lock">
                            <p>🔒 Pro Shorts</p>
                            <button onclick="openModal()">Unlock करें</button>
                        </div>
                    {% else %}
                        <video controls src="/uploads/{{ item.filename }}"></video>
                    {% endif %}
                    <div class="card-info">
                        <div class="card-title">{{ item.title }}</div>
                    </div>
                </div>
                {% endfor %}
            {% endif %}
        </div>
    </div>

    <div class="modal" id="proModal">
        <div class="modal-content">
            <h3>🔥 धूम धड़ाका PRO 💥</h3>
            <p style="margin-top: 10px; font-size: 14px; color: #ccc;">SYED BROTHER VLOG के एक्सक्लूसिव वीडियो के लिए ₹29 पे करें।</p>
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
            if (game.style.display === 'block') {
                game.style.display = 'none';
            } else {
                game.style.display = 'block';
            }
        }

        function filterVideos() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let items = document.getElementsByClassName('video-item');
            for (let item of items) {
                let title = item.getAttribute('data-title');
                if (title.includes(input)) {
                    item.style.display = "block";
                } else {
                    item.style.display = "none";
                }
            }
        }

        function openModal() {
            document.getElementById('proModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('proModal').style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, videos=VIDEOS)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/sw.js')
def service_worker():
    sw_code = """
    const CACHE_NAME = 'dhoom-dhadaka-v3';
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

@app.route('/add-video', methods=['POST'])
def add_video():
    title = request.form.get('title')
    video_type = request.form.get('type')
    is_pro = request.form.get('is_pro') == 'true'

    if 'video_file' not in request.files:
        return redirect(url_for('home'))

    file = request.files['video_file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        VIDEOS.append({
            "id": str(len(VIDEOS) + 1),
            "title": title,
            "filename": filename,
            "type": video_type,
            "is_pro": is_pro
        })

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
