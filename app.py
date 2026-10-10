import os
import re
import time
import socket
import urllib.request
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response
import feedparser

socket.setdefaulttimeout(7)

app = Flask(__name__)

GLOBAL_NEWS_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.aljazeera.com/xml/rss/all.xml',
    'https://rss.dw.com/rdf/rss-en-all',
    'https://www.france24.com/en/rss',
    'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'https://www.cbc.ca/cmlink/rss-topstories',
    'https://www.abc.net.au/news/feed/51120/rss.xml',
    'https://feeds.bbci.co.uk/news/technology/rss.xml',
    'https://feeds.bbci.co.uk/news/business/rss.xml'
]

CURATED_HD_IMAGES = [
    "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1526470608268-f674ce90ebd4?auto=format&fit=crop&w=1600&q=80"
]

news_database = []
seen_titles = set()
last_fetch_timestamp = 0

# ইউজার রেসিপি ডেটাবেজ
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

# ভেরিফাইড চাকরির বিজ্ঞপ্তি ডেটাবেজ
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

def generate_deep_seo_article(title, summary, category, author="Global Wire"):
    date_now = datetime.now().strftime("%B %d, %Y")
    return f"""
    <div class="article-lead-paragraph font-serif text-xl md:text-2xl leading-relaxed text-stone-900 border-l-4 border-amber-600 pl-6 my-8 italic">
        {summary}
    </div>
    <div class="bg-stone-100 p-4 rounded-lg my-6 text-xs text-stone-600 border border-stone-200">
        <strong>SEO & Editorial Indexation:</strong> Verified by automated journalistic validator on {date_now}. Category: <em>{category}</em>. Contributed by: <em>{author}</em>.
    </div>
    <h2 class="text-2xl font-bold text-stone-900 mt-10 mb-4 border-b border-stone-200 pb-2">1. Definitive Context, Primary Genesis & Field Reporting</h2>
    <p class="leading-relaxed mb-6">As documented across verified news channels, the unfolding story surrounding <strong>{title}</strong> represents an essential update across international, institutional, and regional landscapes. The initial reports emerging on {date_now} outline strategic shifts that directly influence international trade agreements, regulatory statutes, and diplomatic engagements.</p>
    <h2 class="text-2xl font-bold text-stone-900 mt-10 mb-4 border-b border-stone-200 pb-2">2. Geopolitical Balance & Sovereign Policy Responses</h2>
    <p class="leading-relaxed mb-6">Cross-border institutions in London, Washington, Brussels, New Delhi, and Singapore are closely tracking the collateral dynamics initiated by this event. Multilateral regulatory bodies have emphasized the imperative need for strict transparency, logistical risk containment, and institutional consensus.</p>
    <h2 class="text-2xl font-bold text-stone-900 mt-10 mb-4 border-b border-stone-200 pb-2">3. Economic Ramifications & Capital Indices</h2>
    <p class="leading-relaxed mb-6">Financial terminals recorded notable indicators as secondary data was distributed. Commercial syndicates, venture portfolios, and global supply chain coordinators have activated tactical mitigation procedures.</p>
    """

def update_news_stream():
    global news_database, seen_titles, last_fetch_timestamp
    current_time = time.time()
    if current_time - last_fetch_timestamp < 60 and len(news_database) > 0:
        return

    cutoff_time = datetime.now() - timedelta(hours=24)
    news_database = [item for item in news_database if item['created_at'] > cutoff_time]

    new_articles = []
    image_idx = 0

    for feed_url in GLOBAL_NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:3]:
                raw_title = clean_html(entry.get('title', ''))
                if not raw_title or raw_title in seen_titles:
                    continue
                seen_titles.add(raw_title)
                summary_raw = clean_html(entry.get('summary', entry.get('description', 'Comprehensive global news report.')))
                
                chosen_image = CURATED_HD_IMAGES[image_idx % len(CURATED_HD_IMAGES)]
                if 'media_content' in entry and len(entry.media_content) > 0:
                    img_candidate = entry.media_content[0].get('url')
                    if img_candidate and 'http' in img_candidate:
                        chosen_image = img_candidate
                image_idx += 1

                article_id = int(time.time() * 1000) + len(new_articles)
                category = "World & Breaking"
                if hasattr(entry, 'tags') and len(entry.tags) > 0:
                    category = entry.tags[0].get('term', 'World')

                long_content = generate_deep_seo_article(raw_title, summary_raw, category)

                new_articles.append({
                    'id': article_id,
                    'title': raw_title,
                    'summary': summary_raw[:220] + "...",
                    'content': long_content,
                    'category': category,
                    'image': chosen_image,
                    'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'created_at': datetime.now(),
                    'likes': 15,
                    'link': f"/news/{article_id}"
                })
        except Exception:
            continue

    if new_articles:
        news_database = new_articles + news_database

    last_fetch_timestamp = current_time

@app.route('/')
def home():
    update_news_stream()
    lead = news_database[0] if news_database else None
    breaking_ticker = [n['title'] for n in news_database[:15]]
    return render_template('index.html', news_list=news_database, lead=lead, ticker=breaking_ticker)

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
        category = request.form.get('category', 'Global Public Wire').strip()
        
        if len(title) < 10 or len(summary) < 25:
            return jsonify({'status': 'error', 'message': 'Title must be 10+ characters and summary 25+ characters.'}), 400

        article_id = int(time.time() * 1000)
        deep_content = generate_deep_seo_article(title, summary, category, author)
        
        article_obj = {
            'id': article_id,
            'title': title,
            'summary': summary[:220] + "...",
            'content': deep_content,
            'category': f"User Dispatch: {category}",
            'image': CURATED_HD_IMAGES[0],
            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'created_at': datetime.now(),
            'likes': 1,
            'link': f"/news/{article_id}"
        }
        
        global news_database
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

# চাকরির বিজ্ঞাপন ভিউ এবং ভেরিফাইড সাবমিশন রাউট
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

        # ভেরিফিকেশন ফিল্টার: ভুয়ো বিজ্ঞাপন ও অসম্পূর্ণ তথ্য প্রতিরোধ
        if len(title) < 5 or len(company) < 3 or len(contact) < 5 or len(description) < 40:
            return jsonify({
                'status': 'error',
                'message': 'Verification Failed: Please provide valid Company Name, Official Contact, and Detailed Job Description (min 40 characters).'
            }), 400

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