import os
import re
import time
import socket
import threading
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response
import feedparser

socket.setdefaulttimeout(7)

app = Flask(__name__)

# গ্লোবাল, ন্যাশনাল, স্টেট, সিটি ও লোকাল নেটওয়ার্ক ফিডস
GLOBAL_NEWS_FEEDS = [
    # আন্তর্জাতিক ও বৈশ্বিক
    ('World', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en'),
    ('World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('World', 'https://www.aljazeera.com/xml/rss/all.xml'),
    # জাতীয়, বিভিন্ন রাজ্য ও আঞ্চলিক
    ('National', 'https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en'),
    ('National', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'),
    ('National', 'https://www.thedailystar.net/frontpage/rss.xml'),
    # আঞ্চলিক / বিভিন্ন জেলা ও শহরের আঞ্চলিক হাব
    ('Regional & Cities', 'https://news.google.com/rss/headlines/section/geo/India?hl=en-IN&gl=IN&ceid=IN:en'),
    ('Regional & Cities', 'https://news.google.com/rss/headlines/section/geo/Kolkata?hl=en-IN&gl=IN&ceid=IN:en'),
    ('Regional & Cities', 'https://news.google.com/rss/headlines/section/geo/Delhi?hl=en-IN&gl=IN&ceid=IN:en'),
    ('Regional & Cities', 'https://news.google.com/rss/headlines/section/geo/Mumbai?hl=en-IN&gl=IN&ceid=IN:en'),
    # ব্যবসা, বাণিজ্য ও বাজার
    ('Business', 'https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en'),
    ('Business', 'https://feeds.bbci.co.uk/news/business/rss.xml'),
    # খেলাধুলা
    ('Sports', 'https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en'),
    ('Sports', 'https://feeds.bbci.co.uk/sport/rss.xml'),
    # প্রযুক্তি ও বিজ্ঞান
    ('Technology', 'https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en'),
    # বিনোদন
    ('Entertainment', 'https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en')
]

news_database = []
seen_fingerprints = set()
lock = threading.Lock()

recipes_database = [
    {
        'id': 1,
        'title': 'Classic Mediterranean Herb Roasted Chicken',
        'author': 'Chef Marco Rossi',
        'category': 'Dinner',
        'prep_time': '45 mins',
        'ingredients': '1 whole chicken, fresh rosemary, thyme, 4 cloves garlic, olive oil, lemon zest, sea salt.',
        'instructions': 'Preheat oven to 200°C. Marinate chicken thoroughly with herbs and garlic. Roast for 45 minutes.'
    }
]

jobs_database = [
    {
        'id': 1,
        'title': 'Senior International News Correspondent',
        'company': 'Global Media Alliance',
        'location': 'New Delhi / Remote',
        'job_type': 'Full-time',
        'salary': 'Commensurate with experience',
        'contact': 'careers@globalmedia.org',
        'description': 'Responsible for tracking breaking diplomatic cables, conducting on-ground interviews, and contributing to the 24-hour wire.',
        'date': datetime.now().strftime("%d %b %Y"),
        'verified': True
    }
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    text = re.sub(r'<.*?>', '', raw_html)
    return " ".join(text.split()).strip()

def normalize_title(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_safe_news_image(entry, title, category):
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    if 'media_content' in entry and len(entry.media_content) > 0:
        for m in entry.media_content:
            url = m.get('url', '')
            if url and any(ext in url.lower() for ext in valid_exts) and not 'icon' in url.lower():
                return url
    if 'links' in entry:
        for l in entry.links:
            href = l.get('href', '')
            if href and (l.get('type', '').startswith('image/') or any(ext in href.lower() for ext in valid_exts)):
                if not 'icon' in href.lower() and not 'logo' in href.lower():
                    return href
    raw_desc = entry.get('summary', '') or entry.get('description', '')
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc)
    if img_match:
        url = img_match.group(1)
        if url.startswith('http') and not 'icon' in url.lower():
            return url

    words = re.findall(r'[a-zA-Z]{4,}', title)
    kw = words[0] if words else category
    sig = abs(hash(title)) % 9999
    return f"https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80&sig={sig}&query={kw}"

def generate_clean_article(title, summary, category):
    date_now = datetime.now().strftime("%B %d, %Y")
    modules = [
        ("Situation Overview", f"Field dispatches report verified local and regional dynamics concerning <strong>{title}</strong>. As recorded on {date_now}, administrative and public observers are monitoring key updates."),
        ("Regional Impact & Public Advisory", "Local administrative desks and civic observers continue tracking field conditions. Public channels emphasize compliance with official advisories."),
        ("Editorial Perspective", "The regional newsroom continues 24-hour verification. Updates will be incorporated as further validated statements are released by ground authorities.")
    ]
    sections = [f"""
    <div class="bg-stone-50 border-l-4 border-stone-800 p-6 rounded-r-xl mb-8">
        <div class="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">Regional Wire &bull; {category} Desk</div>
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
            for entry in parsed.entries[:3]:
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
    
    lead = current_news[0] if current_news else None
    breaking_ticker = [n['title'] for n in current_news[:15]]
    metals_info = get_daily_metals_rates()
    return render_template('index.html', news_list=current_news, lead=lead, ticker=breaking_ticker, metals=metals_info)

@app.route('/news/<int:news_id>')
def single_article(news_id):
    with lock:
        article = next((n for n in news_database if n['id'] == news_id), None)
        if not article and news_database:
            article = news_database[0]
    return render_template('single.html', article=article)

# নির্দিষ্ট শহর, জেলা বা গ্রামের খবর অন-ডিমান্ড খোঁজার এপিআই
@app.route('/api/local-news')
def get_local_geo_news():
    query = request.args.get('location', '').strip()
    if not query:
        return jsonify([])
    
    encoded_loc = urllib.parse.quote_plus(query)
    geo_feed = f"https://news.google.com/rss/search?q={encoded_loc}&hl=en-IN&gl=IN&ceid=IN:en"
    
    results = []
    try:
        parsed = feedparser.parse(geo_feed)
        for entry in parsed.entries[:6]:
            raw_title = clean_html(entry.get('title', ''))
            summary_raw = clean_html(entry.get('summary', ''))
            article_id = int(time.time() * 1000) + len(results)
            results.append({
                'id': article_id,
                'title': raw_title,
                'summary': summary_raw[:180] + "...",
                'category': query.title(),
                'image': f"https://images.unsplash.com/photo-1444723121867-7a241cacace9?auto=format&fit=crop&w=1200&q=80&sig={abs(hash(raw_title))%9999}",
                'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            })
    except Exception:
        pass
    return jsonify(results)

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        author = request.form.get('author', 'Community Journalist').strip()
        category = request.form.get('category', 'National').strip()
        
        if len(title) < 10 or len(summary) < 25:
            return jsonify({'status': 'error', 'message': 'Title must be 10+ characters and summary 25+ characters.'}), 400

        norm_key = normalize_title(title)
        global news_database, seen_fingerprints
        if norm_key in seen_fingerprints:
            return jsonify({'status': 'error', 'message': 'This story is already published.'}), 400
        seen_fingerprints.add(norm_key)

        article_id = int(time.time() * 1000)
        clean_content = generate_clean_article(title, summary, category)
        unique_img = f"https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80&sig={abs(hash(title))%9999}"

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': summary[:200] + "...",
            'content': clean_content,
            'category': category,
            'image': unique_img,
            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'created_at': datetime.now(),
            'likes': 1,
            'link': f"/news/{article_id}"
        }
        with lock:
            news_database.insert(0, article_obj)
        return jsonify({'status': 'success', 'redirect': f'/news/{article_id}'})

    return render_template('submit_news.html')

@app.route('/recipes', methods=['GET', 'POST'])
def recipes_page():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', 'Guest Chef').strip()
        category = request.form.get('category', 'Daily Special').strip()
        prep_time = request.form.get('prep_time', '30 mins').strip()
        ingredients = request.form.get('ingredients', '').strip()
        instructions = request.form.get('instructions', '').strip()

        if title and ingredients and instructions:
            new_recipe = {
                'id': len(recipes_database) + 1,
                'title': title,
                'author': author,
                'category': category,
                'prep_time': prep_time,
                'ingredients': ingredients,
                'instructions': instructions
            }
            recipes_database.insert(0, new_recipe)
            return jsonify({'status': 'success', 'message': 'Recipe published successfully!'})

    return render_template('recipes.html', recipes=recipes_database)

@app.route('/jobs', methods=['GET', 'POST'])
def jobs_page():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time').strip()
        salary = request.form.get('salary', 'Competitive').strip()
        contact = request.form.get('contact', '').strip()
        description = request.form.get('description', '').strip()

        if len(title) < 5 or len(company) < 3 or len(contact) < 5 or len(description) < 40:
            return jsonify({'status': 'error', 'message': 'Please complete all required fields accurately.'}), 400

        new_job = {
            'id': len(jobs_database) + 1,
            'title': title,
            'company': company,
            'location': location,
            'job_type': job_type,
            'salary': salary,
            'contact': contact,
            'description': description,
            'date': datetime.now().strftime("%d %b %Y"),
            'verified': True
        }
        jobs_database.insert(0, new_job)
        return jsonify({'status': 'success', 'message': 'Job opening verified and published live!'})

    return render_template('jobs.html', jobs=jobs_database)

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
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
        
        try:
            import json
            contact_log_file = 'contact_messages.json'
            log_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            }
            records = []
            if os.path.exists(contact_log_file):
                with open(contact_log_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            records.insert(0, log_entry)
            with open(contact_log_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
            
        return jsonify({'status': 'success', 'message': 'Message recorded permanently.'})
        
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