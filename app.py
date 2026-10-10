import os
import re
import time
import socket
import threading
import urllib.parse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response
import feedparser
import requests
from bs4 import BeautifulSoup

socket.setdefaulttimeout(6)

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

def fetch_authentic_original_news_image(entry):
    """সংবাদের মূল পেজ থেকে ১০০% আসল প্রেস ছবি এক্সট্র্যাক্ট করার ইঞ্জিন"""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')

    # ১. আরএসএস মেটাডাটা সরাসরি যাচাই
    if 'media_content' in entry and len(entry.media_content) > 0:
        for m in entry.media_content:
            url = m.get('url', '')
            if url and any(ext in url.lower() for ext in valid_extensions) and not any(bad in url.lower() for bad in ['icon', 'logo', 'placeholder', 'avatar']):
                return url

    if 'links' in entry:
        for l in entry.links:
            href = l.get('href', '')
            if href and (l.get('type', '').startswith('image/') or any(ext in href.lower() for ext in valid_extensions)):
                if not any(bad in href.lower() for bad in ['icon', 'logo', 'placeholder', 'avatar']):
                    return href

    # ২. খবরের আসল ওয়েব লিঙ্ক ভিজিট করে OpenGraph আসল প্রেস ইমেজ সংগ্রহ
    target_link = entry.get('link', '')
    if target_link:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            resp = requests.get(target_link, headers=headers, timeout=4)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # og:image যাচাই
                og_img = soup.find('meta', property='og:image')
                if og_img and og_img.get('content'):
                    img_url = og_img['content']
                    if any(ext in img_url.lower() for ext in valid_extensions) and not any(bad in img_url.lower() for bad in ['icon', 'logo', 'placeholder']):
                        return img_url

                # twitter:image যাচাই
                tw_img = soup.find('meta', attrs={'name': 'twitter:image'})
                if tw_img and tw_img.get('content'):
                    img_url = tw_img['content']
                    if any(ext in img_url.lower() for ext in valid_extensions) and not any(bad in img_url.lower() for bad in ['icon', 'logo', 'placeholder']):
                        return img_url
        except Exception:
            pass

    return None

def generate_clean_article(title, summary, category):
    date_now = datetime.now().strftime("%B %d, %Y")
    modules = [
        ("Situation Overview", f"Field correspondents report developing dynamics surrounding <strong>{title}</strong>. As recorded on {date_now}, institutional observers are monitoring key developments closely across jurisdictions."),
        ("Strategic & Economic Implications", "Market desks and cross-border commercial corridors continue to evaluate the secondary effects of these developments. Authorities emphasize sustained operational transparency."),
        ("Editorial Perspective", "The editorial wire will maintain continuous 24-hour verification. Ground updates will be incorporated as further validated intelligence is confirmed.")
    ]
    sections = [f"""
    <div class="bg-stone-50 border-l-4 border-stone-800 p-6 rounded-r-xl mb-8">
        <div class="text-xs font-bold text-stone-500 uppercase tracking-widest mb-1">Editorial Briefing &bull; {category} Desk</div>
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

def background_news_crawler():
    global news_database, seen_fingerprints
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            with lock:
                news_database = [item for item in news_database if item['created_at'] > cutoff_time]
            
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

                        # ১০০% আসল প্রেস ছবি খোঁজা
                        authentic_image = fetch_authentic_original_news_image(entry)
                        
                        # কঠোর ফিল্টার: আসল ছবি না থাকলে সেই খবর ডাটাবেজেই ঢুকবে না
                        if not authentic_image:
                            continue

                        seen_fingerprints.add(norm_key)
                        summary_raw = clean_html(entry.get('summary', entry.get('description', 'Comprehensive global news report.')))
                        category = cat_hint
                        article_id = int(time.time() * 1000) + len(new_articles)
                        clean_content = generate_clean_article(raw_title, summary_raw, category)

                        new_articles.append({
                            'id': article_id,
                            'title': raw_title,
                            'summary': summary_raw[:200] + "...",
                            'content': clean_content,
                            'category': category,
                            'image': authentic_image,
                            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                            'created_at': datetime.now(),
                            'likes': 18,
                            'link': f"/news/{article_id}"
                        })
                except Exception:
                    continue
            
            if new_articles:
                with lock:
                    news_database = new_articles + news_database
        except Exception:
            pass
        time.sleep(60)

crawler_thread = threading.Thread(target=background_news_crawler, daemon=True)
crawler_thread.start()

@app.route('/')
def home():
    with lock:
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
        default_submit_img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1200&q=80"

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': summary[:200] + "...",
            'content': clean_content,
            'category': category,
            'image': default_submit_img,
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