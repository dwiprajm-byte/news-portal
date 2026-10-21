import os
import re
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_master_auto_wire_2026"

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

    # ব্যাকআপ সমৃদ্ধ নিউজ ফিড (বিভিন্ন ক্যাটাগরির একাধিক তাজা খবর)
    return [
        {
            'id': '501',
            'title': 'Kolkata Metro Expands Intelligent Signaling for High-Frequency Commuter Traffic',
            'summary': 'Kolkata Bureau — Metro railway authorities introduce upgraded rake monitoring systems and automated digital passes to streamline passenger transit across urban corridors.',
            'category': 'Regional',
            'link': '/news/501',
            'image': 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200',
            'published': 'Wed, 21 Oct 2026 08:00:00 GMT'
        },
        {
            'id': '502',
            'title': 'National Green Energy Mission Accelerates Solar Grid Expansion Nationwide',
            'summary': 'New Delhi — Ministry officials review large-scale renewable infrastructure targets, emphasizing decentralized photovoltaic installations and battery storage deployment.',
            'category': 'India',
            'link': '/news/502',
            'image': 'https://images.unsplash.com/photo-1509391365330-2e843beeb9c7?w=800',
            'published': 'Wed, 21 Oct 2026 07:30:00 GMT'
        },
        {
            'id': '503',
            'title': 'Global Semiconductor Supply Chains Stabilize Amid Strong Enterprise Demand',
            'summary': 'Technology Desk — Major microchip fabrication units report consistent output yields, fulfilling industrial requirements for automotive and consumer electronics sectors.',
            'category': 'Technology',
            'link': '/news/503',
            'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
            'published': 'Wed, 21 Oct 2026 07:00:00 GMT'
        },
        {
            'id': '504',
            'title': 'Indian Cricket Squad Finalizes Strategy for Upcoming International Test Series',
            'summary': 'Sports Bureau — National selectors confirm the touring squad following rigorous training sessions, highlighting bowling depth and batting adaptability.',
            'category': 'Sports',
            'link': '/news/504',
            'image': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800',
            'published': 'Wed, 21 Oct 2026 06:30:00 GMT'
        },
        {
            'id': '505',
            'title': 'Global Financial Markets Record Steady Gains Driven by Corporate Earnings',
            'summary': 'Business Wire — Analysts observe resilient trading activity across major exchange indices as multinational corporations release optimistic quarterly forecasts.',
            'category': 'Business',
            'link': '/news/505',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
            'published': 'Wed, 21 Oct 2026 06:00:00 GMT'
        },
        {
            'id': '506',
            'title': 'Agricultural Department Introduces Smart Irrigation Guidelines for Winter Crops',
            'summary': 'West Bengal Desk — Agricultural extension officers conduct regional workshops promoting water-efficient micro-irrigation techniques to maximize crop yields.',
            'category': 'Regional',
            'link': '/news/506',
            'image': 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800',
            'published': 'Wed, 21 Oct 2026 05:30:00 GMT'
        },
        {
            'id': '507',
            'title': 'International Space Research Agency Plans Next-Generation Climate Satellite',
            'summary': 'World Desk — Space scientists unveil advanced orbital payload architectures designed for real-time atmospheric tracking and disaster mitigation support.',
            'category': 'World',
            'link': '/news/507',
            'image': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
            'published': 'Wed, 21 Oct 2026 05:00:00 GMT'
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
            
            is_duplicate = any(clean_news_title(item.get('title', '')) == new_norm for item in all_news)
            
            if not is_duplicate:
                all_news.insert(0, new_article)
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_news[:5000], f, ensure_ascii=False, indent=2)

            return redirect(url_for('home'))
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
