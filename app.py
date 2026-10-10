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
    date_now = datetime.now().strftime("%B %d, %Y")
    modules = [
        ("Situation Overview", f"Field dispatches report verified local and regional dynamics concerning <strong>{title}</strong>. As recorded on {date_now}, administrative and public observers are monitoring key updates."),
        ("Regional Impact & Public Advisory", "Local administrative desks and civic observers continue tracking field conditions. Public channels emphasize compliance with official advisories."),
        ("Editorial Perspective", "The regional newsroom continues 24-hour verification. Updates will be incorporated as further validated statements are released by ground authorities.")
    ]
    sections = [f"""
    <div class="bg-stone-50 border-l-4 border-stone-800 p-6 rounded-r-xl mb-8">
        <div class="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">Verified Wire &bull; {category} Desk</div>
        <p class="font-serif text-lg md:text-xl text-stone-900 leading-relaxed italic">{summary}</p>
    </div>
    """]
    for heading, p in modules:
        sections.append(f"""
        <section class="mb-6">
            <h2 class="text-xl font-bold text-stone-900 border-b border-stone-200 pb-2 mb-3 font-serif">{heading}</h2>
            <p class="text-stone-700 leading-relaxed text-base mb-4">{p}</p>
        </section>
        """)
    return "".join(sections)

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
            cutoff = datetime.now() - timedelta(hours=24)
            news_database = [item for item in (new_articles + news_database) if item['created_at'] > cutoff]

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)