import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# --- PWA Manifest & Service Worker ---
@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "धूम धड़ाका",
        "short_name": "धूम धड़ाका",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#ff0000"
    })

@app.route('/sw.js')
def service_worker():
    return "self.addEventListener('fetch', function(e){});", 200, {'Content-Type': 'application/javascript'}

# --- Main App Interface ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>धूम धड़ाका - SYED BROTHER VLOG</title>
  <link rel="manifest" href="/manifest.json">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, sans-serif; }
    body { background: #000; color: #fff; overflow: hidden; height: 100vh; }
    
    /* Navigation & Search Bar Header */
    .top-header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 50;
      padding: 10px 12px;
      background: rgba(0,0,0,0.95);
      border-bottom: 1px solid #222;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .header-row { display: flex; justify-content: space-between; align-items: center; }
    .logo { color: #ff0000; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; }
    .creator-tag { font-size: 10px; color: #aaa; background: #111; padding: 2px 6px; border-radius: 4px; border: 1px solid #333; }
    
    .search-box-wrap { display: flex; gap: 6px; }
    .search-input { width: 100%; padding: 8px 12px; border-radius: 20px; border: 1px solid #444; background: #1a1a1a; color: #fff; font-size: 13px; outline: none; }
    
    .nav-tabs { display: flex; gap: 8px; justify-content: center; }
    .tab-btn { background: #222; border: none; color: #fff; padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: bold; cursor: pointer; }
    .tab-btn.active { background: #ff0000; }
    
    /* Layout Sections */
    .view-section { display: none; height: 100vh; width: 100vw; }
    .view-section.active { display: block; }

    /* Shorts Feed */
    .shorts-feed { height: 100vh; overflow-y: scroll; scroll-snap-type: y mandatory; }
    .shorts-feed::-webkit-scrollbar { display: none; }
    .short-card { height: 100vh; width: 100vw; scroll-snap-align: start; position: relative; background: #000; display: flex; justify-content: center; align-items: center; }
    
    /* Full Video Grid Feed */
    .full-feed { height: 100vh; overflow-y: auto; padding-top: 100px; padding-bottom: 30px; }
    .video-card { background: #111; margin: 12px; border-radius: 10px; overflow: hidden; border: 1px solid #222; }
    .video-card iframe { width: 100%; height: 210px; border: none; }
    .video-card-info { padding: 10px; }
    .video-card-title { font-size: 14px; font-weight: bold; margin-bottom: 6px; }
    
    iframe { width: 100%; height: 100%; border: none; }
    
    /* Action Sidebar Buttons for Shorts */
    .side-actions { position: absolute; right: 12px; bottom: 40px; z-index: 40; display: flex; flex-direction: column; gap: 18px; align-items: center; }
    .btn-action { background: rgba(30,30,30,0.75); border: none; color: #fff; width: 48px; height: 48px; border-radius: 50%; font-size: 18px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; }
    .btn-action span { font-size: 10px; margin-top: 2px; font-weight: bold; }
    .btn-action.active-like { color: #ff0000; }
    .btn-action.active-dislike { color: #3ea6ff; }
    
    .video-details { position: absolute; left: 15px; bottom: 30px; z-index: 40; max-width: 75%; }
    .channel-info { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    .sub-btn { background: #ff0000; border: none; color: #fff; padding: 6px 14px; border-radius: 18px; font-weight: bold; font-size: 12px; cursor: pointer; }
    .sub-btn.subscribed { background: #333; color: #aaa; }
    
    /* Payment Modal */
    .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 100; justify-content: center; align-items: center; padding: 20px; }
    .modal-box { background: #1f1f1f; padding: 20px; border-radius: 12px; width: 100%; max-width: 320px; text-align: center; border: 1px solid #333; }
    .upi-box { background: #111; border: 2px dashed #22c55e; padding: 10px; border-radius: 8px; margin: 12px 0; color: #22c55e; font-size: 20px; font-weight: bold; }
    .modal-box input { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 6px; border: 1px solid #444; background: #2a2a2a; color: #fff; outline: none; }
    .modal-box button { background: #ff0000; border: none; color: #fff; padding: 10px; border-radius: 6px; width: 100%; font-weight: bold; cursor: pointer; }
  </style>
</head>
<body>

  <!-- Top Header with Navigation & Search -->
  <div class="top-header">
    <div class="header-row">
      <div class="logo">🔥 धूम धड़ाका</div>
      <div class="creator-tag">By SYED BROTHER VLOG (@afaampro15156)</div>
      <button class="tab-btn" style="background:#22c55e;" onclick="openPro()">⭐ ₹29</button>
    </div>
    
    <!-- Search Bar -->
    <div class="search-box-wrap">
      <input type="text" id="searchInput" class="search-input" placeholder="Search SYED BROTHER VLOG, @afaampro15156, Videos..." onkeyup="handleSearch()">
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('shortsTab', this)">🔥 Shorts</button>
      <button class="tab-btn" onclick="switchTab('fullTab', this)">🎬 Full Videos</button>
    </div>
  </div>

  <!-- SECTION 1: SHORTS FEED -->
  <div id="shortsTab" class="view-section active">
    <div class="shorts-feed" id="shortsFeed">
      
      <!-- Short 1 -->
      <div class="short-card" data-title="syed brother vlog @afaampro15156 dhoom dhadaka short video 1">
        <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ?enablejsapi=1&controls=0&loop=1" allow="autoplay"></iframe>
        <div class="video-details">
          <div class="channel-info">
            <b>@afaampro15156</b>
            <button class="sub-btn" onclick="toggleSub(this)">Subscribe</button>
          </div>
          <div>SYED BROTHER VLOG - Special Short #1 🔥</div>
        </div>
        <div class="side-actions">
          <button class="btn-action" onclick="toggleLike(this)">❤️<span class="l-cnt">1.8K</span></button>
          <button class="btn-action" onclick="toggleDislike(this)">👎<span>Dislike</span></button>
          <button class="btn-action" onclick="openComments()">💬<span>Comment</span></button>
          <button class="btn-action" onclick="openPro()">⭐<span>Pro</span></button>
        </div>
      </div>

      <!-- Short 2 -->
      <div class="short-card" data-title="syed brother vlog @afaampro15156 trending short video 2">
        <iframe src="https://www.youtube.com/embed/3JZ_D3ELwOQ?enablejsapi=1&controls=0&loop=1" allow="autoplay"></iframe>
        <div class="video-details">
          <div class="channel-info">
            <b>@afaampro15156</b>
            <button class="sub-btn" onclick="toggleSub(this)">Subscribe</button>
          </div>
          <div>SYED BROTHER VLOG - Trending Short #2 🚀</div>
        </div>
        <div class="side-actions">
          <button class="btn-action" onclick="toggleLike(this)">❤️<span class="l-cnt">4.2K</span></button>
          <button class="btn-action" onclick="toggleDislike(this)">👎<span>Dislike</span></button>
          <button class="btn-action" onclick="openComments()">💬<span>Comment</span></button>
          <button class="btn-action" onclick="openPro()">⭐<span>Pro</span></button>
        </div>
      </div>

    </div>
  </div>

  <!-- SECTION 2: FULL VIDEOS FEED -->
  <div id="fullTab" class="view-section">
    <div class="full-feed" id="fullFeed">
      
      <!-- Full Video 1 -->
      <div class="video-card" data-title="syed brother vlog @afaampro15156 full vlog episode 1">
        <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" allowfullscreen></iframe>
        <div class="video-card-info">
          <div class="video-card-title">SYED BROTHER VLOG - Full Length Episode #1 🎬</div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#aaa;">@afaampro15156 • 25K views</span>
            <button class="sub-btn" onclick="toggleSub(this)">Subscribe</button>
          </div>
        </div>
      </div>

      <!-- Full Video 2 -->
      <div class="video-card" data-title="syed brother vlog @afaampro15156 special movie stream">
        <iframe src="https://www.youtube.com/embed/3JZ_D3ELwOQ" allowfullscreen></iframe>
        <div class="video-card-info">
          <div class="video-card-title">SYED BROTHER VLOG - Special Stream 🌟</div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#aaa;">@afaampro15156 • 88K views</span>
            <button class="sub-btn" onclick="toggleSub(this)">Subscribe</button>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- UPI PAYMENT MODAL -->
  <div class="modal" id="proModal">
    <div class="modal-box">
      <h3>धूम धड़ाका Pro Pass</h3>
      <p style="font-size: 11px; color: #aaa; margin-top: 4px;">Created by SYED BROTHER VLOG (@afaampro15156)</p>
      <p style="font-size: 12px; color: #22c55e; margin-top: 6px; font-weight: bold;">₹29 / Month Ad-Free Feed</p>
      
      <div class="upi-box">
        <div style="font-size: 12px; color: #888;">UPI ID / PhonePe:</div>
        9304040043
      </div>
      
      <input type="text" id="utrInput" placeholder="Enter Transaction / UTR ID">
      <button onclick="submitPayment()">Submit Verification</button>
      <button onclick="closePro()" style="background:#444; margin-top:8px;">Cancel</button>
    </div>
  </div>

  <script>
    function switchTab(tabId, btn) {
      document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');
    }

    function handleSearch() {
      let query = document.getElementById('searchInput').value.toLowerCase().trim();
      let cards = document.querySelectorAll('.short-card, .video-card');
      
      cards.forEach(card => {
        let title = card.getAttribute('data-title').toLowerCase();
        if (title.includes(query) || query === '') {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    function toggleLike(btn) { btn.classList.toggle('active-like'); }
    function toggleDislike(btn) { btn.classList.toggle('active-dislike'); }
    
    function toggleSub(btn) {
      if(btn.innerText === "Subscribe") {
        btn.innerText = "✓ Subscribed";
        btn.classList.add('subscribed');
      } else {
        btn.innerText = "Subscribe";
        btn.classList.remove('subscribed');
      }
    }

    function openComments() {
      let comm = prompt("Apna comment likhein:");
      if(comm) alert("Comment Post Ho Gaya: " + comm);
    }

    function openPro() { document.getElementById('proModal').style.display = 'flex'; }
    function closePro() { document.getElementById('proModal').style.display = 'none'; }
    
    function submitPayment() {
      let val = document.getElementById('utrInput').value;
      if(val) {
        alert("Transaction ID: " + val + " receive ho gaya hai.\nSYED BROTHER VLOG team ise 5 min me verify kar degi!");
        closePro();
      } else {
        alert("Kripya Transaction ID bharein!");
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
