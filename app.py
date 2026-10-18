import os
import time
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = "early_news_master_super_key_2026"

lock = threading.Lock()
news_database = []
DATA_STORE_FILE = "articles_store.json"

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

load_stored_articles()

@app.route('/')
def home():
    global news_database
    current_news = []
    try:
        with lock:
            current_news = list(news_database)
    except Exception:
        current_news = []

    if not current_news:
        current_news = [{
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network',
            'summary': 'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting.',
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }]

    return render_template('index.html', news=current_news, news_list=current_news)

@app.route('/news/<article_id>')
def view_article(article_id):
    target = None
    try:
        with lock:
            for item in news_database:
                if str(item.get('id')) == str(article_id):
                    target = item
                    break
        if not target and os.path.exists(DATA_STORE_FILE):
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
        content = request.form.get('content', '').strip()
        img_url = request.form.get('image_url', '').strip()

        if not title or not content:
            return redirect(url_for('submit_news'))

        is_founder = (author.strip().upper() == 'DWIPRAJ MALLICK')
        if is_founder and founder_pin != "6203":
            return "Security Error: Invalid Founder Passcode.", 403

        article_id = str(int(time.time() * 1000))
        if not img_url:
            img_url = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000'

        article_obj = {
            'id': article_id,
            'title': title,
            'summary': content,
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
