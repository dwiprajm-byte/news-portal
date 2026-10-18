import os
import json
import traceback
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "stable_news_key_2026"

DATA_STORE_FILE = "articles_store.json"

def get_news():
    if os.path.exists(DATA_STORE_FILE):
        try:
            with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.route('/')
def home():
    try:
        articles = get_news()
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
    except Exception as e:
        return f"TEMPLATE RENDERING ERROR: {traceback.format_exc()}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        articles = get_news()
        target = next((item for item in articles if str(item.get('id')) == str(article_id)), None)
        if not target:
            return redirect(url_for('home'))
        return render_template('single.html', article=target)
    except Exception as e:
        return f"ARTICLE PAGE ERROR: {traceback.format_exc()}", 500

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            category = request.form.get('category', 'India').strip()
            location = request.form.get('location', 'Kolkata').strip()
            author = request.form.get('author', '').strip()
            founder_pin = request.form.get('founder_pin', '').strip()
            content = request.form.get('content', '').strip()
            img_url = request.form.get('image_url', '').strip()

            if not title or not content:
                return redirect(url_for('submit_news'))

            if author.strip().upper() == 'DWIPRAJ MALLICK' and founder_pin != "6203":
                return "Security Error: Invalid Founder Passcode.", 403

            article_id = str(int(datetime.now().timestamp() * 1000))
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

            data = get_news()
            data.insert(0, article_obj)
            with open(DATA_STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return redirect(f"/news/{article_id}")
        except Exception as e:
            return f"SUBMISSION ERROR: {traceback.format_exc()}", 500

    return render_template('submit.html')

@app.route('/privacy')
def privacy_page(): return render_template('privacy.html')

@app.route('/about')
def about_page(): return render_template('about.html')

@app.route('/contact')
def contact_page(): return render_template('contact.html')

@app.route('/terms')
def terms_page(): return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt(): return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
