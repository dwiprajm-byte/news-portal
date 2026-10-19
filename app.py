import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_high_volume_scale_key_2026"

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

    # ডিফল্ট হাই-ভলিউম নিউজ ব্যাংক
    return [
        {
            'id': '301',
            'title': '24 Early News High-Volume Wire: 1000+ Daily Verified Dispatches Active',
            'summary': 'Kolkata Newsroom — System successfully scaled to handle high-frequency news ingestion across regional, national, and international categories with strict duplicate prevention.',
            'category': 'India',
            'link': '/news/301',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200',
            'published': 'Mon, 19 Oct 2026 14:30:00 GMT'
        },
        {
            'id': '302',
            'title': 'West Bengal Industrial Corridors Report Surge in MSME Investments',
            'summary': 'Regional Bureau — State commercial centers observe accelerated growth in manufacturing and automotive component distribution networks.',
            'category': 'Regional',
            'link': '/news/302',
            'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800',
            'published': 'Mon, 19 Oct 2026 14:15:00 GMT'
        },
        {
            'id': '303',
            'title': 'Global Technology Giants Unveil AI-Driven Infrastructure Standards',
            'summary': 'Tech Desk — International consortia establish collaborative protocols for secure cloud computing and real-time data processing.',
            'category': 'Technology',
            'link': '/news/303',
            'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
            'published': 'Mon, 19 Oct 2026 14:00:00 GMT'
        },
        {
            'id': '304',
            'title': 'Financial Markets Review: Banking and Energy Stocks Lead Indices',
            'summary': 'Business Desk — Institutional investors maintain positive outlook as corporate earnings reports surpass quarterly projections.',
            'category': 'Business',
            'link': '/news/304',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
            'published': 'Mon, 19 Oct 2026 13:45:00 GMT'
        },
        {
            'id': '305',
            'title': 'National Sports Council Announces New Grassroots Training Facilities',
            'summary': 'Sports Bureau — Multi-discipline athletic complexes planned across semi-urban districts to foster emerging athletic talent.',
            'category': 'Sports',
            'link': '/news/305',
            'image': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800',
            'published': 'Mon, 19 Oct 2026 13:30:00 GMT'
        },
        {
            'id': '306',
            'title': 'International Climate Summit Focuses on Sustainable Urban Planning',
            'summary': 'World Desk — Global delegates deliberate on carbon-neutral construction policies and public transit optimization.',
            'category': 'World',
            'link': '/news/306',
            'image': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
            'published': 'Mon, 19 Oct 2026 13:00:00 GMT'
        }
    ]

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

            all_news = get_articles()
            new_norm = clean_news_title(title)
            
            # ডুপ্লিকেট চেকিং
            is_duplicate = any(clean_news_title(item.get('title', '')) == new_norm for item in all_news)
            
            if not is_duplicate:
                all_news.insert(0, new_article)
                # হাই ভলিউম স্টোরেজ মেইনটেইন করার জন্য মেমরি অপ্টিমাইজড সেভ
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_news[:5000], f, ensure_ascii=False, indent=2)

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
