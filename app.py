import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_master_stable_restore_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def generate_stable_articles():
    categories = ['India', 'World', 'Business', 'Technology', 'Sports', 'Regional']
    bureaus = ['Kolkata Bureau', 'New Delhi Desk', 'Mumbai Financial Wire', 'National Press Service', 'Editorial Desk']
    
    category_images = {
        'India': ["https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1200", "https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1200"],
        'World': ["https://images.unsplash.com/photo-1529101091764-c3526daf38fe?w=1200", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200"],
        'Business': ["https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200"],
        'Technology': ["https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200"],
        'Sports': ["https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200", "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1200"],
        'Regional': ["https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1200", "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200"]
    }

    templates = [
        ("Comprehensive Analysis of National Infrastructure, Digital Growth and Policy Reforms", 
         "An investigative overview examining sweeping economic adjustments, technological integration, and civic development milestones designed to optimize regional productivity and public transparency."),
        ("Global Economic Trends: Market Resilience, Corporate Earnings and Trade Dynamics", 
         "A meticulous financial report reviewing macroeconomic indicators, multinational corporate performance, supply chain efficiencies, and monetary policy adjustments across international exchanges."),
        ("Next-Generation Artificial Intelligence Governance and Cybersecurity Compliance Frameworks", 
         "An extensive examination of emerging regulatory standards for secure cloud computing, data privacy protocols, enterprise automation, and ethical deployment across critical sectors.")
    ]

    base_time = datetime.now()
    all_articles = []
    
    for i in range(1200):
        tmpl = templates[i % len(templates)]
        cat = categories[i % len(categories)]
        bureau = bureaus[i % len(bureaus)]
        
        title = f"{tmpl[0]} — Report Vol. {i+1}" if i > 5 else tmpl[0]
        body = f"{bureau} — {tmpl[1]} Official field dispatches confirm that independent oversight committees are maintaining rigorous scrutiny to ensure absolute compliance with national benchmarks."

        pub_time = base_time - timedelta(minutes=i * 10)
        pool = category_images.get(cat, category_images['India'])
        img = pool[i % len(pool)]

        item = {
            'id': str(16000 + i),
            'title': title,
            'summary': body,
            'category': cat,
            'link': f"/news/{16000 + i}",
            'image': img,
            'published': pub_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        all_articles.append(item)
        
    return all_articles

def get_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if isinstance(items, list) and len(items) > 10:
                    return items
        except Exception:
            pass

    fresh_data = generate_stable_articles()
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(fresh_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return fresh_data

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
                img_url = 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1200'

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
            all_news.insert(0, new_article)
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
