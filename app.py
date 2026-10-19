import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_master_rock_solid_key_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def get_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if isinstance(items, list) and len(items) > 0:
                    return items
        except Exception:
            pass

    return [
        {
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network Live Wire',
            'summary': 'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting across national and international territories.',
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': 'Mon, 19 Oct 2026 13:30:00 GMT'
        },
        {
            'id': '102',
            'title': 'West Bengal Infrastructure & Urban Transit Projects Progress in 2026',
            'summary': 'Kolkata Bureau — State authorities review ongoing roadway and transit development projects to improve connectivity across major regional centers.',
            'category': 'Regional',
            'link': '/news/102',
            'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800',
            'published': 'Mon, 19 Oct 2026 13:15:00 GMT'
        },
        {
            'id': '103',
            'title': 'Global Financial Markets & Technology Stocks Show Steady Movement',
            'summary': 'Mumbai Desk — Analysts observe stable trading across key indices as technological innovations drive enterprise investment trends.',
            'category': 'Business',
            'link': '/news/103',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
            'published': 'Mon, 19 Oct 2026 13:00:00 GMT'
        },
        {
            'id': '104',
            'title': 'Digital Telecommunications & Artificial Intelligence Policy Updates',
            'summary': 'New Delhi — Regulatory authorities issue framework recommendations regarding digital safety and responsible technology integration.',
            'category': 'Technology',
            'link': '/news/104',
            'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
            'published': 'Mon, 19 Oct 2026 12:45:00 GMT'
        },
        {
            'id': '105',
            'title': 'National Sports Federation Outlines Preparations for Upcoming Tournament',
            'summary': 'Sports Desk — Athletes begin rigorous camp training as the national federation finalizes squad selections for regional championships.',
            'category': 'Sports',
            'link': '/news/105',
            'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
            'published': 'Mon, 19 Oct 2026 12:30:00 GMT'
        }
    ]

def save_article_without_duplicate(new_article):
    try:
        all_news = get_articles()
        new_norm = clean_news_title(new_article['title'])
        
        # ডুপ্লিকেট টাইটেল রোধ
        for item in all_news:
            if clean_news_title(item.get('title', '')) == new_norm:
                return False
                
        all_news.insert(0, new_article)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_news, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

@app.route('/')
def home():
    try:
        articles = get_articles()
        return render_template('index.html', news=articles, news_list=articles)
    except Exception as e:
        return f"CRITICAL RENDER ERROR: {str(e)}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        articles = get_articles()
        target = next((item for item in articles if str(item.get('id')) == str(article_id)), articles[0])
        return render_template('single.html', article=target)
    except Exception:
        return redirect(url_for('home'))

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

            new_id = str(int(datetime.now().timestamp() * 1000))
            if not img_url:
                img_url = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000'

            new_article = {
                'id': new_id,
                'title': title,
                'summary': content,
                'category': category,
                'link': f"/news/{new_id}",
                'image': img_url,
                'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }

            save_article_without_duplicate(new_article)
            return redirect(f"/news/{new_id}")
        except Exception as e:
            return f"Submission Error: {str(e)}", 500

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
