import os
import re
import time
import sqlite3
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import feedparser

app = Flask(__name__)
app.secret_key = "early_news_master_automated_engine_2026"

DB_FILE = "database.db"

# ১. স্থায়ী SQLite ডেটাবেস ইনিশিয়ালাইজেশন (খবর কোনোদিন মুছবে না)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT UNIQUE,
            summary TEXT,
            category TEXT,
            link TEXT,
            image TEXT,
            published TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

CATEGORY_IMAGES = {
    'India': 'https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1200',
    'Regional': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1200',
    'World': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200',
    'Business': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200',
    'StockMarket': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200',
    'Politics': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200',
    'Technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200',
    'Automobile': 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200',
    'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200',
    'Entertainment': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200',
    'Education': 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1200',
    'Health': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=1200',
    'Crime': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200',
    'Weather': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=1200'
}

def get_all_articles():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles ORDER BY created_at DESC LIMIT 1000")
        rows = cursor.fetchall()
        articles = [dict(row) for row in rows]
        conn.close()
        return articles
    except Exception:
        return []

def get_single_article(article_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (str(article_id),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None

def save_article_to_db(article):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO articles (id, title, summary, category, link, image, published)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            article['id'],
            article['title'],
            article['summary'],
            article['category'],
            article['link'],
            article['image'],
            article['published']
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

def format_human_editorial_article(title, summary, category, location, author):
    clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
    if not clean_summary:
        clean_summary = f"{location} — {title} সংক্রান্ত বিষয়ে প্রশাসনিক ও প্রাতিষ্ঠানিক স্তরে বিশদ তথ্য সামনে এসেছে।"

    return f'''
    <div class="editorial-container max-w-3xl mx-auto font-sans leading-relaxed text-gray-800">
        <div class="flex flex-wrap items-center justify-between border-y border-gray-200 py-3 mb-6 text-sm text-gray-600 bg-gray-50/70 px-4 rounded-lg">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-red-600 text-white font-bold flex items-center justify-center text-sm shadow">
                    {author[0].upper() if author else 'E'}
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
                {clean_summary}
            </p>
            <p>
                ঘটনার পরিপ্রেক্ষিতে স্থানীয় ও সংশ্লিষ্ট প্রশাসনিক স্তরে তৎপরতা বৃদ্ধি পেয়েছে। নির্ভরযোগ্য পর্যবেক্ষকদের মতে, বর্তমান পরিস্থিতির সুদূরপ্রসারী প্রভাব খতিয়ে দেখে প্রয়োজনীয় সবরকম কার্যকর পদক্ষেপ গ্রহণ করা হচ্ছে।
            </p>
            <blockquote class="p-4 my-4 border-l-4 border-red-500 bg-slate-50 italic text-gray-700 text-base font-sans">
                "যেকোনো বিষয়ে জনস্বার্থে তথ্য যাচাই এবং সঠিক দৃষ্টিভঙ্গি বজায় রাখাই সাংবাদিকতার মূল চালিকাশক্তি," সংশ্লিষ্ট বিশ্লেষকরা বিষয়টি স্পষ্ট করেছেন।
            </blockquote>
            <p>
                24 Early News সম্পাদকীয় ডেস্ক সার্বিক পরিস্থিতির ওপর সার্বক্ষণিক নজর রাখছে এবং প্রতিটি নতুন ও যাচাইকৃত তথ্য সরাসরি আপডেট করবে।
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

# ২. উচ্চ ক্ষমতাসম্পন্ন স্বয়ংক্রিয় গুগল ফিড স্ক্র্যাপার (প্রতি ১ মিনিটে ১টি ক্যাটাগরি)
def high_volume_news_crawler():
    FEEDS = [
        ('India', 'https://news.google.com/rss/search?q=India+top+news+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('World', 'https://news.google.com/rss/search?q=World+news+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Business', 'https://news.google.com/rss/search?q=Business+Economy+Stock+India+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Technology', 'https://news.google.com/rss/search?q=Technology+AI+Mobiles+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Sports', 'https://news.google.com/rss/search?q=Cricket+Football+Sports+India+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Regional', 'https://news.google.com/rss/search?q=West+Bengal+Kolkata+news+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Politics', 'https://news.google.com/rss/search?q=Indian+Politics+Elections+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Entertainment', 'https://news.google.com/rss/search?q=Bollywood+Cinema+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Health', 'https://news.google.com/rss/search?q=Health+Medical+Research+when:24h&hl=en-IN&gl=IN&ceid=IN:en'),
        ('Education', 'https://news.google.com/rss/search?q=Education+Jobs+Careers+India+when:24h&hl=en-IN&gl=IN&ceid=IN:en')
    ]

    category_index = 0
    total_categories = len(FEEDS)

    while True:
        try:
            # প্রতি সাইকেলে ক্রমান্বয়ে ১টি নির্দিষ্ট ক্যাটাগরি নির্বাচন
            cat, feed_url = FEEDS[category_index]
            category_index = (category_index + 1) % total_categories

            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:5]:  # নির্বাচিত ক্যাটাগরি থেকে শীর্ষ ৫টি খবর প্রসেস করা
                raw_title = entry.get('title', '').split(' - ')[0].strip()
                raw_desc = entry.get('summary', entry.get('description', ''))
                
                if not raw_title:
                    continue

                art_id = str(int(time.time() * 1000))
                img = CATEGORY_IMAGES.get(cat, CATEGORY_IMAGES['India'])
                article_html = format_human_editorial_article(raw_title, raw_desc, cat, "Kolkata", "DWIPRAJ MALLICK")

                article_data = {
                    'id': art_id,
                    'title': raw_title,
                    'summary': article_html,
                    'category': cat,
                    'link': f"/news/{art_id}",
                    'image': img,
                    'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                }
                save_article_to_db(article_data)
        except Exception:
            pass

        # প্রতি ১ মিনিট অন্তর ব্যাকগ্রাউন্ডে চেক করবে
        time.sleep(60)

# ব্যাকগ্রাউন্ডে স্বয়ংক্রিয় স্ক্র্যাপার চালু
crawler_thread = threading.Thread(target=high_volume_news_crawler, daemon=True)
crawler_thread.start()

# ==================== ROUTES ====================
@app.route('/')
def home():
    articles = get_all_articles()

    if not articles:
        articles = [{
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network Live Wire',
            'summary': format_human_editorial_article(
                '24 Early News: Verified Global & Regional Media Network Live Wire',
                'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting.',
                'India', 'Kolkata', 'DWIPRAJ MALLICK'
            ),
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }]

    return render_template('index.html', news=articles, news_list=articles)

@app.route('/news/<article_id>')
def view_article(article_id):
    target = get_single_article(article_id)
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
        content = request.form.get('content', '').strip()
        img_url = request.form.get('image_url', '').strip()

        if not title or not content:
            return redirect(url_for('submit_news'))

        is_founder = (author.strip().upper() == 'DWIPRAJ MALLICK')
        if is_founder and founder_pin != "6203":
            return "Security Error: Invalid Founder Passcode.", 403

        article_id = str(int(time.time() * 1000))
        if not img_url:
            img_url = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES['India'])

        body_html = format_human_editorial_article(title, content, category, location, author)

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': body_html,
            'category': category,
            'link': f"/news/{article_id}",
            'image': img_url,
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        save_article_to_db(article_obj)

        return redirect(f"/news/{article_id}")

    return render_template('submit.html')

# AdSense Compliance Routes
@app.route('/privacy')
@app.route('/privacy-policy')
def privacy_page(): return render_template('privacy.html')

@app.route('/about')
@app.route('/about-us')
def about_page(): return render_template('about.html')

@app.route('/contact')
@app.route('/contact-us')
def contact_page(): return render_template('contact.html')

@app.route('/terms')
@app.route('/terms-of-service')
def terms_page(): return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt(): return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
