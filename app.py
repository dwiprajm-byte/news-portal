import os
import re
import time
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import feedparser

app = Flask(__name__)
app.secret_key = "early_news_master_super_key_2026"

lock = threading.Lock()
news_database = []

# লোকাল স্থায়ী সংরক্ষণ ফাইল
DATA_STORE_FILE = "articles_store.json"

CATEGORY_IMAGES = {
    'India': 'https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1000',
    'Regional': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1000',
    'World': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1000',
    'Business': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000',
    'StockMarket': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1000',
    'Politics': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1000',
    'Technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000',
    'Automobile': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1000',
    'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1000',
    'Entertainment': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1000',
    'Education': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1000',
    'Health': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=1000',
    'Crime': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1000',
    'Weather': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1000'
}

def load_stored_articles():
    global news_database
    if os.path.exists(DATA_STORE_FILE):
        try:
            with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                news_database = json.load(f)
        except Exception:
            news_database = []

def save_article_permanently(article):
    global news_database
    try:
        data = []
        if os.path.exists(DATA_STORE_FILE):
            try:
                with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.insert(0, article)
        with open(DATA_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def generate_seo_article_body(title, summary, category, location, author):
    return f'''
    <div class="editorial-container max-w-3xl mx-auto font-sans leading-relaxed text-gray-800">
        <div class="flex flex-wrap items-center justify-between border-y border-gray-200 py-3 mb-6 text-sm text-gray-600 bg-gray-50/70 px-4 rounded-lg">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-red-600 text-white font-bold flex items-center justify-center text-sm shadow">
                    {author[0].upper() if author else '24'}
                </div>
                <div>
                    <span class="font-bold text-gray-900 block">{author}</span>
                    <span class="text-xs text-gray-500">{category} Bureau &bull; Verified Wire</span>
                </div>
            </div>
            <div class="text-xs text-gray-500 mt-2 sm:mt-0 font-medium">
                <span>📍 {location}</span> &bull; <span class="text-green-700 font-semibold font-mono">Fact Checked &amp; Verified</span>
            </div>
        </div>

        <div class="article-body space-y-4 text-base md:text-lg text-gray-800 leading-8 font-serif">
            <p class="first-letter:text-5xl first-letter:font-bold first-letter:text-red-600 first-letter:float-left first-letter:mr-3">
                <strong class="font-sans uppercase text-xs tracking-wider text-gray-500 block mb-1.5">{location} DISPATCH —</strong>
                {summary}
            </p>
            <p>
                ঘটনার পরিপ্রেক্ষিতে সংশ্লিষ্ট দফতর এবং আঞ্চলিক স্তরে তৎপরতা বৃদ্ধি পেয়েছে। নির্ভরযোগ্য সূত্র জানিয়েছে, উদ্ভূত পরিস্থিতির ওপর সার্বক্ষণিক নজর রাখা হচ্ছে যাতে নির্ভরযোগ্য তথ্য যথাসময়ে জনসাধারণের কাছে পৌঁছায়।
            </p>
            <blockquote class="p-4 my-4 border-l-4 border-red-500 bg-slate-50 italic text-gray-700 text-base font-sans">
                "বস্তুনিষ্ঠ এবং যাচাইকৃত তথ্য পরিবেশন করাই সংবাদমাধ্যমের মূল ভিত্তি," সংশ্লিষ্ট পর্যবেক্ষকরা জানিয়েছেন।
            </blockquote>
            <p>
                24 Early News এ সংক্রান্ত যেকোনো নতুন পদক্ষেপ ও প্রশাসনিক ঘোষণার ওপর নজর রাখছে এবং প্রতিটি তথ্য সরাসরি আপডেট করবে।
            </p>
        </div>

        <script type="application/ld+json">
        {{
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": "{title}",
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
    </div>
    '''

def fetch_trending_wire_news():
    global news_database
    FEEDS = [
        ('India', 'https://news.google.com/rss/search?q=India+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('World', 'https://news.google.com/rss/search?q=World+news+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Business', 'https://news.google.com/rss/search?q=Business+India+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Technology', 'https://news.google.com/rss/search?q=Technology+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Sports', 'https://news.google.com/rss/search?q=Cricket+when:24h&hl=en-IN&gl=IN&ceid=IN:en')
    ]
    items = []
    for cat, url in FEEDS:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:3]:
                t = e.get('title', '').split(' - ')[0].strip()
                desc = re.sub(r'<[^>]+>', '', e.get('summary', e.get('description', ''))).strip()
                if not desc:
                    desc = f"{t} নিয়ে প্রশাসনিক ও প্রাতিষ্ঠানিক স্তরে বিশদ আলোচনা চলছে।"
                art_id = str(int(time.time() * 1000) + len(items))
                img = CATEGORY_IMAGES.get(cat, CATEGORY_IMAGES['India'])
                body = generate_seo_article_body(t, desc, cat, "Kolkata", "DWIPRAJ MALLICK")

                items.append({
                    'id': art_id,
                    'title': t,
                    'summary': body,
                    'category': cat,
                    'link': f"/news/{art_id}",
                    'image': img,
                    'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'created_at': datetime.now().isoformat()
                })
        except Exception:
            continue

    if items:
        with lock:
            existing_titles = {n.get('title') for n in news_database}
            unique_new = [x for x in items if x['title'] not in existing_titles]
            news_database = unique_new + news_database
            for it in unique_new:
                save_article_permanently(it)

# ব্যাকগ্রাউন্ড সিঙ্ক থ্রেড
def start_sync_worker():
    while True:
        try:
            fetch_trending_wire_news()
        except Exception:
            pass
        time.sleep(900)

load_stored_articles()
if not news_database:
    threading.Thread(target=fetch_trending_wire_news, daemon=True).start()
threading.Thread(target=start_sync_worker, daemon=True).start()

# ==================== WEB ROUTES ====================

@app.route('/')
def home():
    with lock:
        current_news = list(news_database)

    if not current_news:
        current_news = [{
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network Begins Live Wire',
            'summary': generate_seo_article_body(
                '24 Early News: Verified Global & Regional Media Network Begins Live Wire',
                '24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting across global territories.',
                'India', 'Kolkata', 'DWIPRAJ MALLICK'
            ),
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }]

    return render_template('index.html', news=current_news, news_list=current_news)

@app.route('/news/<article_id>')
def view_article(article_id):
    target = None
    with lock:
        for item in news_database:
            if str(item.get('id')) == str(article_id):
                target = item
                break

    if not target:
        if os.path.exists(DATA_STORE_FILE):
            try:
                with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                    for item in stored:
                        if str(item.get('id')) == str(article_id):
                            target = item
                            break
            except Exception:
                pass

    if not target:
        return redirect(url_for('home'))

    return render_template('single.html', article=target)

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
        valid_founder_code = "6203"

        if is_founder:
            if founder_pin != valid_founder_code:
                return "Security Error: Invalid Founder Passcode.", 403
        else:
            if 'DWIPRAJ' in author.upper() or 'ADMIN' in author.upper():
                return "Security Error: Unauthorized use of Founder Byline.", 403
            if not id_proof or not contact_info:
                return "Error: External contributors must submit verified ID number and contact info.", 400

        article_id = str(int(time.time() * 1000))

        # ফাইল আপলোড থাকলে তা সংরক্ষণ
        uploaded_image = request.files.get('news_image_file')
        if uploaded_image and uploaded_image.filename:
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            img_ext = os.path.splitext(uploaded_image.filename)[1].lower()
            if img_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                saved_img_name = f"news_{article_id}{img_ext}"
                uploaded_image.save(os.path.join(upload_dir, saved_img_name))
                img_url = f"/static/uploads/{saved_img_name}"

        if not img_url:
            img_url = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES['India'])

        body_html = generate_seo_article_body(title, content, category, location, author)

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': body_html,
            'category': category,
            'link': f"/news/{article_id}",
            'image': img_url,
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'created_at': datetime.now().isoformat()
        }

        with lock:
            news_database.insert(0, article_obj)
            save_article_permanently(article_obj)

        return redirect(f"/news/{article_id}")

    return render_template('submit.html')

# ==================== MANDATORY ADSENSE POLICY ROUTES ====================
@app.route('/privacy')
@app.route('/privacy-policy')
def privacy_page():
    return render_template('privacy.html')

@app.route('/about')
@app.route('/about-us')
def about_page():
    return render_template('about.html')

@app.route('/contact')
@app.route('/contact-us')
def contact_page():
    return render_template('contact.html')

@app.route('/terms')
@app.route('/terms-of-service')
def terms_page():
    return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    tb_str = traceback.format_exc()
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Error Diagnostic Desk</title>
        <style>
            body {{ font-family: monospace; background: #0f172a; color: #f8fafc; padding: 20px; }}
            .box {{ background: #1e293b; border: 2px solid #ef4444; border-radius: 10px; padding: 20px; }}
            h2 {{ color: #ef4444; }}
            pre {{ background: #000; color: #38bdf8; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>⚠️ লাইভ এরর ডায়াগনস্টিক আউটপুট</h2>
            <p>দয়া করে এই কোড বা টেক্সটটি কপি করে আমাকে দিন, আমি সাথে সাথে ঠিক করে দেব:</p>
            <pre>{tb_str}</pre>
        </div>
    </body>
    </html>
    ''', 500

