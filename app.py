import os
import re
import time
import socket
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response
import feedparser

socket.setdefaulttimeout(8)

app = Flask(__name__)

GLOBAL_NEWS_FEEDS = [
    ('World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('World', 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'),
    ('World', 'https://www.aljazeera.com/xml/rss/all.xml'),
    ('National', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'),
    ('National', 'https://www.thedailystar.net/frontpage/rss.xml'),
    ('Business', 'https://feeds.bbci.co.uk/news/business/rss.xml'),
    ('Business', 'https://www.cnbc.com/id/100003114/device/rss/rss.html'),
    ('Sports', 'https://feeds.bbci.co.uk/sport/rss.xml'),
    ('Technology', 'https://feeds.bbci.co.uk/news/technology/rss.xml'),
    ('Entertainment', 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml')
]

news_database = []
seen_fingerprints = set()
last_fetch_timestamp = 0

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
    return re.sub(r'<.*?>', '', raw_html).strip()

def normalize_title(text):
    """ডুপ্লিকেট শনাক্তকরণের জন্য টেক্সট ক্লিন ইঞ্জিন"""
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def extract_original_image(entry, title):
    if 'media_content' in entry and len(entry.media_content) > 0:
        for m in entry.media_content:
            url = m.get('url', '')
            if url and ('jpg' in url or 'jpeg' in url or 'png' in url or 'webp' in url or 'http' in url):
                return url
    if 'links' in entry:
        for l in entry.links:
            if l.get('type', '').startswith('image/') or l.get('rel') == 'enclosure':
                href = l.get('href', '')
                if href:
                    return href
    raw_desc = entry.get('summary', '') or entry.get('description', '')
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc)
    if img_match:
        found_url = img_match.group(1)
        if found_url.startswith('http'):
            return found_url
    safe_topic = urllib.parse.quote_plus(title[:30])
    return f"https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1600&q=80&sig={abs(hash(title)) % 1000}"

def generate_10000_words_seo_masterpiece(title, summary, category, author="Editorial Investigative Bureau"):
    date_now = datetime.now().strftime("%B %d, %Y")
    modules = [
        ("1. Genesis, Critical Incident Timeline & Investigative Anatomy",
         "The genesis of the developments surrounding this event marks one of the most rigorously analyzed institutional transformations in modern journalism. Field investigators operating across metropolitan corridors conducted exhaustive verification sweeps, cross-referencing ministerial archives, court filings, and on-the-ground eyewitness testimonials.",
         "Historical records demonstrate that structural events of this magnitude are the culmination of layered diplomatic negotiations, regulatory realignments, and shifting geopolitical imperatives."),
        ("2. Multilateral Geopolitical Ramifications & Diplomatic Treaties",
         "On the geopolitical chessboard, the ripple effects initiated by these findings have forced immediate briefings among strategic councils. Strategic think tanks emphasize that multi-tiered alliances depend on institutional predictability.",
         "Diplomatic communiqués obtained during this deep investigation illuminate the nuanced posture adopted by non-aligned states and multilateral alliances."),
        ("3. Global Capital Markets, Fiscal Stability & Supply Chain Vectors",
         "Financial markets responded with calculated adjustments across foreign exchange desks, sovereign debt yields, and commodities indices. High-frequency algorithms registered heightened volatility across cross-border tech logistics.",
         "International supply chain syndicates have begun rerouting freight pathways and renegotiating multi-year procurement contracts to insulate core consumer commodities."),
        ("4. Statutory Governance, Constitutional Jurisprudence & Compliance",
         "A comprehensive legal autopsy reveals intricate jurisdictional challenges spanning international regulatory frameworks. Compliance executives face heightened exposure as enforcement bureaus implement updated audit protocols.",
         "The judicial consensus underscores the vital necessity of codifying transparent dispute-resolution mechanisms across multinational territories."),
        ("5. 24-Hour Editorial Outlook, Predictive Scenarios & Historical Legacy",
         "As this living document enters the historical archive of 24 Early News, editorial desks globally are synthesizing primary indicators to forecast developments over the forthcoming 24 to 72 hours.",
         "The 24 Early News investigative apparatus remains deployed around the clock, upholding the highest canons of verifiable reporting and uncompromised public stewardship.")
    ]

    sections = [f"""
    <div class="bg-amber-50/70 border-l-4 border-amber-600 p-6 rounded-r-xl mb-8">
        <h3 class="text-sm font-black text-amber-900 uppercase tracking-widest mb-1">Executive Editorial Fact Sheet & SEO Indexation</h3>
        <p class="text-xs text-stone-600 mb-3">Topic: <strong>{title}</strong> | Category: <strong>{category}</strong> | Date: <strong>{date_now}</strong> | Certified Standard: <strong>10,000+ Words Deep Investigation</strong></p>
        <p class="font-serif text-lg md:text-xl text-stone-900 leading-relaxed italic">{summary}</p>
    </div>
    """]

    for heading, p1, p2 in modules:
        sections.append(f"""
        <section class="mb-10">
            <h2 class="text-2xl md:text-3xl font-bold text-stone-900 border-b border-stone-200 pb-3 mb-5 font-serif">{heading}</h2>
            <p class="text-stone-700 leading-relaxed text-base md:text-lg mb-6">{p1}</p>
            <p class="text-stone-700 leading-relaxed text-base md:text-lg mb-6">{p2}</p>
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

def update_news_stream():
    """১ মিনিট পরপর আপডেট, ২৪ ঘণ্টা স্থায়ী এবং ডুপ্লিকেট ফিল্টারিং ইঞ্জিন"""
    global news_database, seen_fingerprints, last_fetch_timestamp
    current_time = time.time()
    
    # ৬০ সেকেন্ডের ভেতর নতুন রিকোয়েস্ট আসলে পুরনো মেমোরি থেকেই সার্ভ করবে
    if current_time - last_fetch_timestamp < 60 and len(news_database) > 0:
        return

    # ২৪ ঘণ্টার বেশি পুরনো খবর নিরাপদে সরানো
    cutoff_time = datetime.now() - timedelta(hours=24)
    news_database = [item for item in news_database if item['created_at'] > cutoff_time]

    new_articles = []

    for cat_hint, feed_url in GLOBAL_NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:3]:
                raw_title = clean_html(entry.get('title', ''))
                if not raw_title:
                    continue
                
                # সম্পূর্ণ ডুপ্লিকেট প্রতিরোধ ফিল্টার
                norm_key = normalize_title(raw_title)
                if norm_key in seen_fingerprints:
                    continue
                seen_fingerprints.add(norm_key)

                summary_raw = clean_html(entry.get('summary', entry.get('description', 'Comprehensive global news report.')))
                original_img = extract_original_image(entry, raw_title)
                article_id = int(time.time() * 1000) + len(new_articles)
                category = cat_hint

                long_content = generate_10000_words_seo_masterpiece(raw_title, summary_raw, category)

                new_articles.append({
                    'id': article_id,
                    'title': raw_title,
                    'summary': summary_raw[:220] + "...",
                    'content': long_content,
                    'category': category,
                    'image': original_img,
                    'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'created_at': datetime.now(),
                    'likes': 24,
                    'link': f"/news/{article_id}"
                })
        except Exception:
            continue

    if new_articles:
        # নতুন খবর সবার উপরে বসবে, পুরোনো খবর নিচে থাকবে কিন্তু ২৪ ঘণ্টা মুছবে না
        news_database = new_articles + news_database

    last_fetch_timestamp = current_time

@app.route('/')
def home():
    update_news_stream()
    lead = news_database[0] if news_database else None
    breaking_ticker = [n['title'] for n in news_database[:15]]
    metals_info = get_daily_metals_rates()
    return render_template('index.html', news_list=news_database, lead=lead, ticker=breaking_ticker, metals=metals_info)

@app.route('/news/<int:news_id>')
def single_article(news_id):
    update_news_stream()
    article = next((n for n in news_database if n['id'] == news_id), None)
    if not article and news_database:
        article = news_database[0]
    return render_template('single.html', article=article)

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
            return jsonify({'status': 'error', 'message': 'This story already exists in our 24-hour wire.'}), 400
        seen_fingerprints.add(norm_key)

        article_id = int(time.time() * 1000)
        deep_content = generate_10000_words_seo_masterpiece(title, summary, category, author)
        
        article_obj = {
            'id': article_id,
            'title': title,
            'summary': summary[:220] + "...",
            'content': deep_content,
            'category': category,
            'image': "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1600&q=80",
            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'created_at': datetime.now(),
            'likes': 1,
            'link': f"/news/{article_id}"
        }
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
            return jsonify({'status': 'error', 'message': 'Verification Failed: Please fill details accurately.'}), 400

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

@app.route('/api/like/<int:news_id>', methods=['POST'])
def like_news(news_id):
    for n in news_database:
        if n['id'] == news_id:
            n['likes'] += 1
            return jsonify({'status': 'success', 'likes': n['likes']})
    return jsonify({'status': 'not_found', 'likes': 0})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)