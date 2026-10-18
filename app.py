import os
import time
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "early_news_absolute_stable_key_2026"

DATA_STORE_FILE = "articles_store.json"

def get_all_news():
    if os.path.exists(DATA_STORE_FILE):
        try:
            with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_news(article):
    try:
        data = get_all_news()
        data.insert(0, article)
        with open(DATA_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

@app.route('/')
def home():
    articles = get_all_news()
    if not articles:
        articles = [{
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network',
            'summary': 'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting.',
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }]
    return render_template('index.html', news=articles, news_list=articles)

@app.route('/news/<article_id>')
def view_article(article_id):
    articles = get_all_news()
    target = next((item for item in articles if str(item.get('id')) == str(article_id)), None)
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

        save_news(article_obj)
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
