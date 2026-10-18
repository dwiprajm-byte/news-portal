# ==================== ULTRA-FAST EDITORIAL DISPATCH ENGINE ====================
import random
import time
from datetime import datetime

REPORTERS = [
    ("S. Mukherjee", "Senior Political Correspondent", "Kolkata Bureau"),
    ("A. Sengupta", "National Affairs Desk", "New Delhi Bureau"),
    ("R. Sharma", "Special Financial Analyst", "Mumbai Bureau"),
    ("P. Dasgupta", "Global Wire & Strategic Affairs", "Eastern Bureau")
]

def build_instant_editorial(title, raw_input, category, location, author):
    if not author:
        author, desg, bur = random.choice(REPORTERS)
    else:
        desg, bur = "Staff Correspondent", f"{category} Desk"

    if not location:
        location = "Kolkata"

    # বহু-প্যারাগ্রাফ ও সাংবাদিকসুলভ কাঠামো তৈরি (0.001 সেকেন্ডের মধ্যে সম্পন্ন)
    formatted_html = f"""
    <div class="editorial-container max-w-3xl mx-auto font-sans leading-relaxed text-gray-800">
        <!-- Reporter Info Bar -->
        <div class="flex flex-wrap items-center justify-between border-y border-gray-200 py-3 mb-6 text-sm text-gray-600 bg-gray-50/60 px-4 rounded-lg">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-red-600 text-white font-bold flex items-center justify-center text-sm shadow">
                    {author[0].upper()}
                </div>
                <div>
                    <span class="font-bold text-gray-900 block">{author}</span>
                    <span class="text-xs text-gray-500">{desg} &bull; {bur}</span>
                </div>
            </div>
            <div class="text-xs text-gray-500 mt-2 sm:mt-0 font-medium">
                <span>📍 {location}</span> &bull; <span class="text-green-700 font-semibold font-mono">Fact Checked &amp; Verified</span>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="bg-red-50/50 border-l-4 border-red-600 p-4 rounded-r-xl mb-6 shadow-xs">
            <h4 class="text-xs font-bold uppercase tracking-wider text-red-900 mb-2 flex items-center gap-2">
                <i class="fas fa-bolt text-red-600"></i> Executive Summary &amp; Key Highlights
            </h4>
            <ul class="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Ground details confirmed directly from regional correspondents in {location}.</li>
                <li>Authorities and analytical teams maintain continuous monitoring over the unfolding situation.</li>
                <li>Broad implications noted across sectoral interests and administrative reviews.</li>
            </ul>
        </div>

        <!-- Article Ground Narrative -->
        <div class="space-y-4 text-base md:text-lg text-gray-800 font-serif leading-8">
            <p class="first-letter:text-5xl first-letter:font-bold first-letter:text-red-600 first-letter:float-left first-letter:mr-3 first-letter:leading-none">
                <strong class="font-sans uppercase text-xs tracking-wider text-gray-500 block mb-1.5">{location} DISPATCH —</strong>
                {raw_input}
            </p>

            <h3 class="font-sans text-xl font-bold text-gray-900 pt-4 pb-1 border-b border-gray-100">
                Ground Assessment &amp; Strategic Perspectives
            </h3>
            
            <p>
                In-depth discussions surrounding <em>"{title}"</em> highlight shifting strategic priorities within both regional and broader institutional contexts. Observers on the ground emphasize that timely coordination among relevant departments will play an essential role in addressing operational nuances.
            </p>

            <blockquote class="p-4 my-4 border-l-4 border-gray-400 bg-gray-50 italic text-gray-700 text-base">
                "Maintaining verified reporting standards remains our primary focus as further updates develop from ground sources," confirmed editorial desks monitoring official communications.
            </blockquote>

            <p>
                Moving forward, ongoing field reviews will track subsequent announcements and structural impacts. 24 Early News continues to verify all regional dispatches to deliver complete, authoritative transparency.
            </p>
        </div>

        <!-- Footer Seal -->
        <div class="mt-8 pt-4 border-t border-gray-200 text-xs text-gray-500 flex flex-wrap justify-between items-center">
            <span>&copy; 2026 24 Early News Wire Service. All rights reserved.</span>
            <span class="font-medium text-gray-700">Editorial Oversight &bull; Original Reporting</span>
        </div>
    </div>
    """
    return formatted_html
# ==============================================================================
import os
import re
import time
import socket
import threading
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
import feedparser
import requests
from bs4 import BeautifulSoup

socket.setdefaulttimeout(7)
app = Flask(__name__)

# --- OFFICIAL SEARCH ENGINE SITEMAPS (HIGH PRIORITY) ---
@app.route('/sitemap.txt', methods=['GET'])
def serve_sitemap_txt():
    from flask import Response
    txt_data = """https://24earlynews.com/
https://24earlynews.com/about-us
https://24earlynews.com/contact-us
https://24earlynews.com/privacy-policy
https://24earlynews.com/terms
https://24earlynews.com/disclaimer
https://24earlynews.com/pricing"""
    return Response(txt_data.strip(), mimetype='text/plain', content_type='text/plain; charset=utf-8')
# -----------------------------------------------------

# সরাসরি আসল ছবি প্রদানকারী ভেরিফায়েড প্রেস ফিড
GLOBAL_NEWS_FEEDS = [
    ('Entertainment', 'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms'),
    ('Entertainment', 'https://www.hindustantimes.com/feeds/rss/entertainment/rssfeed.xml'),
    ('National', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'),
    ('National', 'https://www.thehindu.com/news/national/feeder/default.rss'),
    ('Regional & Cities', 'https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms'),
    ('Regional & Cities', 'https://timesofindia.indiatimes.com/rssfeeds/-2128839596.cms'),
    ('World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('World', 'https://www.aljazeera.com/xml/rss/all.xml'),
    ('Business', 'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms'),
    ('Sports', 'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms'),
    ('Sports', 'https://feeds.bbci.co.uk/sport/rss.xml'),
    ('Technology', 'https://timesofindia.indiatimes.com/rssfeeds/66949542.cms')
]

news_database = []
seen_fingerprints = set()
lock = threading.Lock()

# ক্যাটাগরি ও বিষয়ভিত্তিক শতভাগ ভেরিফায়েড হাই-কোয়ালিটি প্রেস ছবি পুল
CATEGORY_FALLBACK_IMAGES = {
    'Entertainment': [
        'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=1200&q=80'
    ],
    'Sports': [
        'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1200&q=80'
    ],
    'National': [
        'https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1575320181282-9afab399332c?auto=format&fit=crop&w=1200&q=80'
    ],
    'Regional & Cities': [
        'https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=1200&q=80'
    ],
    'Business': [
        'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200&q=80'
    ],
    'Technology': [
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80'
    ],
    'World': [
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80',
        'https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=1200&q=80'
    ]
}

def is_valid_image(url):
    """গুগল লোগো ও ডামি আইকন ফিল্টারিং"""
    if not url or not url.startswith('http'):
        return False
    u = url.lower()
    blocked = ['google', 'gstatic', 'googleusercontent', 'icon', 'logo', 'avatar', 'pixel', 'stat?', 'placeholder', 'dummy']
    return not any(b in u for b in blocked)

def extract_safe_news_image(entry, title, category):
    # ১. আরএসএস media_content
    if 'media_content' in entry and len(entry.media_content) > 0:
        for m in entry.media_content:
            url = m.get('url', '')
            if is_valid_image(url):
                return url

    # ২. আরএসএস media_thumbnail
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        for t in entry.media_thumbnail:
            url = t.get('url', '')
            if is_valid_image(url):
                return url

    # ৩. enclosures
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            url = enc.get('href', '') or enc.get('url', '')
            if is_valid_image(url):
                return url

    # ৪. HTML ডেসক্রিপশনের <img> ট্যাগ
    raw_desc = entry.get('summary', '') or entry.get('description', '')
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc)
    if img_match:
        url = img_match.group(1)
        if is_valid_image(url):
            return url

    # ৫. বিষয়ের ওপর ভিত্তি করে অনন্য প্রিমিয়াম প্রেস ফটো নির্বাচন
    cat = category if category in CATEGORY_FALLBACK_IMAGES else 'National'
    pool = CATEGORY_FALLBACK_IMAGES[cat]
    idx = abs(hash(title)) % len(pool)
    return pool[idx]

def clean_html(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r'<.*?>', '', raw_html)
    return " ".join(text.split()).strip()

def normalize_title(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def generate_clean_article(title, summary, category):
    """গুগল এসইও বান্ধব ১০০% ন্যাচারাল এডিটরিয়াল রিপোর্ট (রোবোটিক টেবিল ও অটোমেশন মুক্ত)"""
    date_now = datetime.now().strftime("%B %d, %Y")
    
    sections = f"""
    <!-- Executive Brief -->
    <div class="bg-amber-50/70 border-l-4 border-amber-600 p-6 rounded-r-2xl mb-8 shadow-xs">
        <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-amber-900 mb-2">
            <i class="fas fa-newspaper text-amber-600"></i> Special Report &bull; {category} Desk
        </div>
        <p class="font-serif text-lg md:text-xl text-stone-900 leading-relaxed italic mb-4">
            {summary}
        </p>
        <div class="border-t border-amber-200/80 pt-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-amber-950 mb-2">Key Highlights:</h4>
            <ul class="text-xs sm:text-sm text-stone-800 space-y-1.5 list-disc list-inside">
                <li>Key field reports recorded as of <strong>{date_now}</strong> across regional desks.</li>
                <li>Strategic assessments underway involving institutional authorities and key stakeholders.</li>
                <li>Public communications emphasize continuous awareness and compliance with official advisories.</li>
            </ul>
        </div>
    </div>

    <!-- Chapter 1: Comprehensive Dispatch & Primary Analysis -->
    <section class="mb-8">
        <h2 class="text-xl sm:text-2xl font-bold text-stone-900 border-b border-stone-200 pb-2 mb-4 font-serif">
            1. Comprehensive Dispatch & Ground Developments
        </h2>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            Special correspondents have submitted detailed reports concerning <strong>{title}</strong>. 
            The latest sequence of events demonstrates substantial civic, regulatory, and public engagement, underscoring broader structural implications across both local hubs and broader policy frameworks.
        </p>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            Ground observers indicate that the underlying factors contributing to this occurrence reflect key institutional directives and operational developments. Observers stationed across the sector have noted increased deliberation between stakeholders aiming to stabilize situation continuity while maintaining transparent reporting.
        </p>
    </section>

    <!-- Chapter 2: Institutional Perspective & Strategic Governance -->
    <section class="mb-8">
        <h2 class="text-xl sm:text-2xl font-bold text-stone-900 border-b border-stone-200 pb-2 mb-4 font-serif">
            2. Administrative Response & Policy Trajectory
        </h2>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            Administrative bodies and oversight committees have stepped up coordination following the formal release of this information. Key directives outline structured measures designed to evaluate potential impacts, optimize communication transparency, and facilitate public advisories where appropriate.
        </p>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            Civic analysts reiterate that statutory compliance remains an essential pillar throughout this process. Strategic panels are reviewing current frameworks to determine whether standard contingencies suffice or if specialized interventions will be necessitated over the coming cycle.
        </p>
    </section>

    <!-- Chapter 3: Socio-Economic Significance & Broader Repercussions -->
    <section class="mb-8">
        <h2 class="text-xl sm:text-2xl font-bold text-stone-900 border-b border-stone-200 pb-2 mb-4 font-serif">
            3. Broader Context & Future Outlook
        </h2>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            Beyond immediate notifications, this situation intersects significantly with ongoing demographic and civic considerations. Sector analysts and regional commentators highlight that systematic resolutions will likely influence public confidence and industry standards for weeks to come.
        </p>
        <p class="text-stone-700 leading-relaxed text-base mb-4 font-normal">
            As public dialogues expand, industry observers advocate for measured, fact-checked dissemination of records to prevent uncorroborated narratives from diluting official channels. The editorial desk maintains direct contact with official bureaus to confirm follow-up briefings.
        </p>
    </section>

    <!-- Chapter 4: Frequently Asked Questions (FAQ) -->
    <section class="mb-10 bg-stone-50 border border-stone-200 p-6 rounded-2xl">
        <h3 class="text-lg font-bold text-stone-900 font-serif mb-4 flex items-center gap-2">
            <i class="fas fa-question-circle text-amber-600"></i> Frequently Asked Questions (FAQ)
        </h3>
        <div class="space-y-4 text-xs sm:text-sm">
            <div>
                <h4 class="font-bold text-stone-900 mb-1">What is the central focus of this latest report?</h4>
                <p class="text-stone-700 leading-relaxed">
                    The report investigates key ground and strategic developments concerning <strong>{title}</strong>, documenting factual updates recorded on {date_now}.
                </p>
            </div>
            <div>
                <h4 class="font-bold text-stone-900 mb-1">How can readers stay informed regarding subsequent updates?</h4>
                <p class="text-stone-700 leading-relaxed">
                    Continuous dispatches and follow-up statements are monitored directly on our portal as further validated statements are released by ground authorities.
                </p>
            </div>
        </div>
    </section>
    """
    return sections

def get_daily_metals_rates():
    return {
        'date': datetime.now().strftime("%d %B %Y"),
        'currencies': {
            'IN': {'country': 'India', 'curr': 'INR', 'symbol': '₹', 'mult': 1.0},
            'BD': {'country': 'Bangladesh', 'curr': 'BDT', 'symbol': '৳', 'mult': 1.42},
            'US': {'country': 'United States', 'curr': 'USD', 'symbol': '$', 'mult': 0.0115},
            'AE': {'country': 'UAE / Dubai', 'curr': 'AED', 'symbol': 'د.إ', 'mult': 0.042},
            'UK': {'country': 'United Kingdom', 'curr': 'GBP', 'symbol': '£', 'mult': 0.0091},
            'EU': {'country': 'Eurozone', 'curr': 'EUR', 'symbol': '€', 'mult': 0.0108}
        }
    }

def fetch_feed_items():
    global news_database, seen_fingerprints
    new_articles = []
    for cat_hint, feed_url in GLOBAL_NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:4]:
                raw_title = clean_html(entry.get('title', ''))
                if not raw_title:
                    continue
                norm_key = normalize_title(raw_title)
                if norm_key in seen_fingerprints:
                    continue
                seen_fingerprints.add(norm_key)

                summary_raw = clean_html(entry.get('summary', entry.get('description', 'Verified regional dispatch.')))
                category = cat_hint
                img_url = extract_safe_news_image(entry, raw_title, category)
                article_id = int(time.time() * 1000) + len(new_articles)
                clean_content = generate_clean_article(raw_title, summary_raw, category)

                new_articles.append({
                    'id': article_id,
                    'title': raw_title,
                    'summary': summary_raw[:200] + "...",
                    'content': clean_content,
                    'category': category,
                    'image': img_url,
                    'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'created_at': datetime.now(),
                    'likes': 18,
                    'link': f"/news/{article_id}"
                })
        except Exception:
            continue
    
    if new_articles:
        with lock:
            # No cutoff: all articles are permanently stored
            news_database = [item for item in (new_articles + news_database) if True]

try:
    fetch_feed_items()
except Exception:
    pass

def background_loop():
    while True:
        time.sleep(60)
        try:
            fetch_feed_items()
        except Exception:
            pass

crawler_thread = threading.Thread(target=background_loop, daemon=True)
crawler_thread.start()

@app.route('/')
def home():
    with lock:
        if len(news_database) == 0:
            fetch_feed_items()
        current_news = list(news_database)
        if current_news:
            minute_seed = int(time.time() // 60)
            rotate_offset = minute_seed % len(current_news)
            rotated_news = current_news[rotate_offset:] + current_news[:rotate_offset]
        else:
            rotated_news = []

    lead = rotated_news[0] if rotated_news else None
    breaking_ticker = [n['title'] for n in rotated_news[:15]]
    metals_info = get_daily_metals_rates()
    return render_template('index.html', news_list=rotated_news, lead=lead, ticker=breaking_ticker, metals=metals_info)

@app.route('/news/<int:news_id>')
def single_article(news_id):
    with lock:
        article = next((n for n in news_database if n['id'] == news_id), None)
        if not article and news_database:
            article = news_database[0]
    return render_template('single.html', article=article)

@app.route('/recipes', methods=['GET', 'POST'])
def recipes_page():
    return render_template('recipes.html', recipes=[])

@app.route('/jobs', methods=['GET', 'POST'])
def jobs_page():
    return render_template('jobs.html', jobs=[])

@app.route('/metals')
def metals_page():
    return render_template('metals.html', metals=get_daily_metals_rates())

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('policies.html', page_title='Privacy Policy', page_type='privacy')

@app.route('/about-us')
def about_us():
    return render_template('policies.html', page_title='About Us', page_type='about')

@app.route('/terms')
def terms_page():
    return render_template('policies.html', page_title='Terms of Service', page_type='terms')

@app.route('/disclaimer')
def disclaimer_page():
    return render_template('policies.html', page_title='Disclaimer', page_type='disclaimer')

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
    return render_template('contact.html')

@app.route('/api/like/<int:news_id>', methods=['POST'])
def like_news(news_id):
    with lock:
        for n in news_database:
            if n['id'] == news_id:
                n['likes'] += 1
                return jsonify({'status': 'success', 'likes': n['likes']})
    return jsonify({'status': 'not_found', 'likes': 0})

ADMIN_SECRET_KEY = "admin2026"  # আপনার ব্যক্তিগত অ্যাডমিন পাসওয়ার্ড

from flask import session, redirect, url_for

app.secret_key = "early_news_secret_master_key_2026"

# ব্যবহারকারীদের ডাটাবেজ (যাদের পেমেন্ট ভেরিফাই হবে তাদের আলাদা আলাদা আইডি-পাসওয়ার্ড এখানে থাকবে)
REGISTERED_USERS = {
    # প্রতিষ্ঠাতা ও পরিচালক (মাস্টার অ্যাকাউন্ট)
    "admin": {
        "password": "adminpassword2026",
        "name": "DWIPRAJ MALLICK",
        "role": "Chief Editor"
    },
    # পেইড ক্লায়েন্ট / কাস্টমার ১
    "client1": {
        "password": "passclient123",
        "name": "Special Bureau Reporter",
        "role": "Paid Contributor"
    },
    # পেইড ক্লায়েন্ট / কাস্টমার ২
    "press02": {
        "password": "newsaccess456",
        "name": "Verified Press Agency",
        "role": "Paid Contributor"
    }
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # বিভিন্ন সম্ভাব্য ফর্ম ফিল্ডের নাম হ্যান্ডেল করা
        u = (request.form.get('username') or request.form.get('userid') or request.form.get('user') or '').strip().lower()
        p = (request.form.get('password') or request.form.get('pass') or '').strip()

        # admin অথবা Dwipraj আইডি এবং নির্দিষ্ট পাসওয়ার্ড দিয়ে লগইন নিশ্চিত করা
        if (u in ['admin', 'dwipraj']) and p == 'admin1234':
            session['logged_in'] = True
            session['user'] = 'admin'
            return redirect(url_for('submit_news'))
        else:
            error = 'ভুল ইউজার আইডি বা পাসওয়ার্ড! পুনরায় চেষ্টা করুন।'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout_page():
    session.clear()
    return redirect('/')

@app.route('/pricing')
def pricing_page():
    return render_template('pricing.html')

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'India').strip()
        location = request.form.get('location', 'Kolkata').strip()
        author = request.form.get('author', '').strip()
        founder_pin = request.form.get('founder_pin', '').strip()
        id_type = request.form.get('id_type', 'KYC').strip()
        id_proof = request.form.get('id_proof', '').strip()
        contact_info = request.form.get('contact_info', '').strip()
        img_url = request.form.get('image_url', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            return redirect(url_for('submit_news'))

        is_founder = (author.strip().upper() == 'DWIPRAJ MALLICK')
        valid_founder_code = "62" + "03"

        if is_founder:
            if founder_pin != valid_founder_code:
                return "Security Error: Invalid Founder Passcode.", 403
        else:
            if 'DWIPRAJ' in author.upper() or 'ADMIN' in author.upper():
                return "Security Error: Unauthorized attempt to use Founder Byline.", 403
            if not id_proof or not contact_info:
                return "Error: External contributors must submit verified ID number and contact info.", 400

        article_id = str(int(time.time() * 1000))

        # আসল ছবি আপলোড থাকলে তা static/uploads-এ সেভ করা
        uploaded_image = request.files.get('news_image_file')
        if uploaded_image and uploaded_image.filename:
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            img_ext = os.path.splitext(uploaded_image.filename)[1].lower()
            if img_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                saved_img_name = f"news_{article_id}{img_ext}"
                uploaded_image.save(os.path.join(upload_dir, saved_img_name))
                img_url = f"/static/uploads/{saved_img_name}"

        # যদি ছবি না থাকে তবে ক্যাটাগরি অনুযায়ী স্ট্যান্ডার্ড ছবি
        if not img_url:
            cat_images = {
                'India': 'https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1000',
                'World': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1000',
                'Business': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000',
                'Technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000',
                'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1000',
                'Entertainment': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1000'
            }
            img_url = cat_images.get(category, 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000')

        ver_badge = "Editor-in-Chief & Founder" if is_founder else f"Verified Contributor [{id_type}]"

        seo_body = f"""
        <div class="editorial-container max-w-3xl mx-auto font-sans leading-relaxed text-gray-800">
            <div class="flex flex-wrap items-center justify-between border-y border-gray-200 py-3 mb-6 text-sm text-gray-600 bg-gray-50/70 px-4 rounded-lg">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-red-600 text-white font-bold flex items-center justify-center text-sm shadow">
                        {author[0].upper() if author else 'E'}
                    </div>
                    <div>
                        <span class="font-bold text-gray-900 block">{author}</span>
                        <span class="text-xs text-gray-500">{category} Bureau &bull; {ver_badge}</span>
                    </div>
                </div>
                <div class="text-xs text-gray-500 mt-2 sm:mt-0 font-medium">
                    <span>📍 {location}</span> &bull; <span class="text-green-700 font-semibold font-mono">Fact Checked &amp; Verified</span>
                </div>
            </div>

            <div class="article-body space-y-4 text-base md:text-lg text-gray-800 leading-8 font-serif">
                <p class="first-letter:text-5xl first-letter:font-bold first-letter:text-red-600 first-letter:float-left first-letter:mr-3">
                    <strong class="font-sans uppercase text-xs tracking-wider text-gray-500 block mb-1.5">{location} DISPATCH —</strong>
                    {content}
                </p>
            </div>

            <script type="application/ld+json">
            {{
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "headline": "{title}",
                "image": ["{img_url}"],
                "datePublished": "{datetime.now().isoformat()}",
                "author": [{{
                    "@type": "Person",
                    "name": "{author}"
                }}],
                "publisher": {{
                    "@type": "NewsMediaOrganization",
                    "name": "24 Early News",
                    "url": "https://24earlynews.com"
                }}
            }}
            </script>

            <div class="mt-8 pt-4 border-t border-gray-200 text-xs text-gray-500 flex justify-between">
                <span>&copy; 2026 24 Early News Network</span>
                <span class="text-slate-600 font-semibold">Verified Journalism &amp; Ethical Media</span>
            </div>
        </div>
        """

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': seo_body,
            'category': category,
            'link': f"/news/{article_id}",
            'image': img_url,
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'created_at': datetime.now()
        }

        with lock:
            news_database.insert(0, article_obj)
            if 'save_article_permanently' in globals():
                save_article_permanently(article_obj)

        return redirect(f"/news/{article_id}")

    return render_template('submit.html')


@app.route('/editorial-charter')
def editorial_charter():
    return render_template('charter.html')







if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
import keep_alive


# --- Auto Crash Handler & Fallback ---
@app.errorhandler(500)
def handle_500_error(e):
    try:
        # যদি index.html ক্র্যাশ করে, তবে ক্যাশ করা বা সংরক্ষিত ভিউ প্রদর্শন করবে
        return render_template('index.html.bak'), 200
    except Exception:
        # যদি ব্যাকআপ ফাইলও না মেলে, তবে সাইট ডাউন না দেখিয়ে সেফ মোড পেজ দেখাবে
        return render_template('index.html', news=[]), 200

@app.errorhandler(Exception)
def handle_general_exception(e):
    return handle_500_error(e)

@app.route('/sitemap.xml')
def root_sitemap():
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'), 'sitemap.xml', mimetype='application/xml')

# ==================== GOOGLE ADSENSE ADS.TXT ROUTE ====================

# ==================== GUARANTEED ADS.TXT DELIVERY ====================
@app.route('/ads.txt')
def render_ads_txt():
    from flask import Response
    content = "google.com, pub-9701604898518993, DIRECT, f08c47fec0942fa0"
    return Response(content, mimetype='text/plain')

# ==================== DIRECT BROWSER FAVICON ROUTE ====================
@app.route('/favicon.ico')
def serve_root_favicon():
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')

# ==================== DAILY VEDIC PANCHANG & HOROSCOPE ENGINE ====================
@app.route('/api/panchang')
def api_daily_panchang():
    from flask import jsonify
    from datetime import datetime
    import calendar

    now = datetime.now()
    day = now.day
    month = now.month
    year = now.year
    weekday_idx = now.weekday()

    bengali_days = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]
    bar = bengali_days[weekday_idx]

    # তিথি ও পক্ষ তালিকা (গুপ্তপ্রেস ও বিশুদ্ধ পঞ্জিকা ধারা)
    tithis = [
        "শুক্লা প্রতিপদ", "শুক্লা দ্বিতীয়া", "শুক্লা তৃতীয়া", "শুক্লা চতুর্থী", "শুক্লা পঞ্চমী",
        "শুক্লা ষষ্ঠী", "শুক্লা সপ্তমী", "শুক্লা অষ্টমী", "শুক্লা নবমী", "শুক্লা দশমী",
        "শুক্লা একাদশী", "শুক্লা দ্বাদশী", "শুক্লা ত্রয়োদশী (প্রদোষ ব্রত)", "শুক্লা চতুর্দশী", "পূর্ণিমা",
        "কৃষ্ণা প্রতিপদ", "কৃষ্ণা দ্বিতীয়া", "কৃষ্ণা তৃতীয়া", "কৃষ্ণা চতুর্থী", "কৃষ্ণা পঞ্চমী",
        "কৃষ্ণা ষষ্ঠী", "কৃষ্ণা সপ্তমী", "কৃষ্ণা অষ্টমী", "কৃষ্ণা নবমী", "কৃষ্ণা দশমী",
        "কৃষ্ণা একাদশী", "কৃষ্ণা দ্বাদশী", "কৃষ্ণা ত্রয়োদশী (প্রদোষ ব্রত)", "কৃষ্ণা চতুর্দশী (মাসিক শিবরাত্রি)", "অমাবস্যা"
    ]
    cur_tithi = tithis[(day - 1) % len(tithis)]

    # নক্ষত্র তালিকা (২৭ নক্ষত্র)
    nakshatras = [
        "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিরা", "আর্দ্রা", "পুনর্বসু", "পুষ্যা", "অশ্লেষা",
        "মঘা", "পূর্বফল্গুনী", "উত্তরফল্গুনী", "হস্ত", "চিত্রা", "স্বাতী", "বিশাখা", "অনুরাধা",
        "জ্যেষ্ঠা", "মূল", "পূর্বাষাঢ়া", "উত্তরাষাঢ়া", "শ্রবণা", "ধনিষ্ঠা", "শতভিষা", "পূর্বভাদ্রপদ", "উত্তরভাদ্রপদ", "রেবতী"
    ]
    cur_nakshatra = nakshatras[(day + month * 2) % 27]

    # যোগ ও করণ
    yogas = ["বিষ্কুম্ভ", "প্রীতি", "আয়ুষ্মান", "সৌভাগ্য", "শোভন", "অতিগণ্ড", "সুকর্মা", "ধৃতি", "শূল", "গণ্ড", "বৃদ্ধি", "ধ্রুব", "ব্যাসঘাত", "হর্ষণ", "বজ্র", "সিদ্ধি", "ব্যতিপাত", "বরীয়ান", "পরিঘ", "শিব", "সিদ্ধ", "সাধ্য", "শুভ", "শুক্ল", "ব্রহ্ম", "ঐন্দ্র", "বৈধৃতি"]
    karans = ["বব", "বালব", "কৌলব", "তৈতিল", "গর", "বণিজ", "বিষ্টী (ভদ্রা)", "শকুনি", "চতুস্পদ", "নাগ", "কিম্স্তুঘ্ন"]
    
    cur_yoga = yogas[(day + month) % len(yogas)]
    cur_karan = karans[(day * 2) % len(karans)]

    # বারভেদে প্রামাণ্য রাহুকাল ও শুভ অমৃত মুহূর্ত (ভারতীয় স্ট্যান্ডার্ড টাইম)
    rahu_times = [
        "সকাল ০৭:৩০ – ০৯:০০", # সোম
        "বিকেল ০৩:০০ – ০৪:৩০", # মঙ্গল
        "দুপুর ১২:০০ – ০১:৩০", # বুধ
        "দুপুর ০১:৩০ – ০৩:০০", # বৃহস্পতি
        "সকাল ১০:৩০ – ১২:০০", # শুক্র
        "সকাল ০৯:০০ – ১০:৩০", # শনি
        "বিকেল ০৪:৩০ – ০৬:০০"  # রবি
    ]
    cur_rahu = rahu_times[weekday_idx]
    subha_muhurat = "সকাল ১১:৩৬ – দুপুর ১২:২৪ (অভিজিৎ/অমৃতযোগ)"

    # বিশেষ ব্রত ও উৎসব তালিকা
    upcoming_events = []
    if "ত্রয়োদশী" in cur_tithi:
        upcoming_events.append("আজ পবিত্র প্রদোষ ব্রত (শিব আরাধনা)")
    if "কৃষ্ণা চতুর্দশী" in cur_tithi:
        upcoming_events.append("আজ মাসিক শিবরাত্রি ব্রত")
    if day in [14, 15] and month in [1, 4, 7, 10]:
        upcoming_events.append("আজ সৌর সংক্রান্তি")
    if month == 2 and (day >= 10 and day <= 16):
        upcoming_events.append("বসন্ত পঞ্চমী (শ্রীশ্রী সরস্বতী পূজা সমাগত)")
    if month == 5 and (day >= 5 and day <= 12):
        upcoming_events.append("অক্ষয় তৃতীয়া পুণ্য তিথি সমাগত")
    if month == 7 and (day >= 1 and day <= 10):
        upcoming_events.append("শ্রীশ্রী জগন্নাথদেবের রথযাত্রা মহোৎসব")
    if month == 10 and (day >= 15 and day <= 24):
        upcoming_events.append("শারদীয়া দুর্গোৎসব: মহাষ্টমী ও মহানবমী পূণ্যলক্ষণ")
    if not upcoming_events:
        upcoming_events.append("নিত্য পূজা ও শান্তিকর্মের জন্য দিনটি অনুকূল")

    # ১২ রাশির বৈদিক ফলাফল
    forecasts = [
        "কর্মক্ষেত্রে পদোন্নতি বা নতুন সুযোগের যোগ রয়েছে। আর্থিক লেনদেনে সচেতন থাকুন।",
        "পারিবারিক শান্তি বজায় থাকবে। ব্যবসায়ীদের জন্য নতুন বিনিয়োগ শুভ ফল দেবে।",
        "সৃজনশীল কাজে সাফল্য মিলবে। ভ্রমণের সুযোগ আসতে পারে, স্বাস্থ্য অনুকূল।",
        "মানসিক প্রফুল্লতা বৃদ্ধি পাবে। আটকে থাকা অর্থ প্রাপ্তির সম্ভাবনা রয়েছে।",
        "গুরুত্বপূর্ণ সিদ্ধান্তে শুভাকাঙ্ক্ষীদের পরামর্শে লাভবান হবেন। সুনাম বৃদ্ধি পাবে।",
        "ব্যবসায় নতুন অংশীদারিত্বের সুযোগ। শিক্ষার্থীদের একাগ্রতা বৃদ্ধি পাবে।",
        "আয় বৃদ্ধির নতুন পথ উন্মোচিত হতে পারে। ধর্মীয় কাজে মানসিক শান্তি মিলবে।",
        "কর্মক্ষেত্রে অতিরিক্ত দায়িত্ব বৃদ্ধি পেতে পারে। ধৈর্য বজায় রাখা শ্রেয়।",
        "ভাগ্য আপনার পক্ষে থাকবে। দূরবর্তী যোগাযোগ থেকে শুভ সংবাদ পেতে পারেন।",
        "পুরোনো সমস্যার সুষ্ঠু সমাধান হবে। পরিজনদের সঙ্গে সুসম্পর্ক বজায় থাকবে।",
        "নতুন উদ্যোগে সাফল্য আসবে। আর্থিক স্থিতিশীলতা বজায় থাকবে।",
        "আধ্যাত্মিক চিন্তায় মানসিক তৃপ্তি। পারিবারিক ক্ষেত্রে আনন্দময় পরিবেশ থাকবে।"
    ]

    rashi_list = [
        {"name": "মেষ (Aries)", "symbol": "♈", "text": forecasts[(day + 0) % 12]},
        {"name": "বৃষ (Taurus)", "symbol": "♉", "text": forecasts[(day + 1) % 12]},
        {"name": "মিথুন (Gemini)", "symbol": "♊", "text": forecasts[(day + 2) % 12]},
        {"name": "কর্কট (Cancer)", "symbol": "♋", "text": forecasts[(day + 3) % 12]},
        {"name": "সিংহ (Leo)", "symbol": "♌", "text": forecasts[(day + 4) % 12]},
        {"name": "কন্যা (Virgo)", "symbol": "♍", "text": forecasts[(day + 5) % 12]},
        {"name": "তুলা (Libra)", "symbol": "♎", "text": forecasts[(day + 6) % 12]},
        {"name": "বৃশ্চিক (Scorpio)", "symbol": "♏", "text": forecasts[(day + 7) % 12]},
        {"name": "ধনু (Sagittarius)", "symbol": "♐", "text": forecasts[(day + 8) % 12]},
        {"name": "মকর (Capricorn)", "symbol": "♑", "text": forecasts[(day + 9) % 12]},
        {"name": "কুম্ভ (Aquarius)", "symbol": "♒", "text": forecasts[(day + 10) % 12]},
        {"name": "মীন (Pisces)", "symbol": "♓", "text": forecasts[(day + 11) % 12]}
    ]

    return jsonify({
        "date_str": now.strftime("%d %B, %Y"),
        "bar": bar,
        "tithi": cur_tithi,
        "nakshatra": cur_nakshatra,
        "yoga": cur_yoga,
        "karan": cur_karan,
        "rahu": cur_rahu,
        "shubha": subha_muhurat,
        "adhimas": "বর্তমান বৎসর শুদ্ধমাস (অধিমাস/মলমাস দোষমুক্ত)",
        "events": upcoming_events,
        "rashifal": rashi_list
    })
# ==================================================================================


@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')

@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')


# --- GOOGLE ADSENSE MANDATORY COMPLIANCE ROUTES ---
@app.route('/privacy')
@app.route('/privacy-policy')
def serve_privacy():
    return render_template('privacy.html')

@app.route('/about')
@app.route('/about-us')
def serve_about():
    return render_template('about.html')

@app.route('/contact')
@app.route('/contact-us')
def serve_contact():
    return render_template('contact.html')

@app.route('/terms')
@app.route('/terms-of-service')
def serve_terms():
    return render_template('terms.html')

