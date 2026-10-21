import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_safe_clean_secure_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def generate_safe_professional_news():
    categories = ['India', 'World', 'Business', 'Technology', 'Sports', 'Regional']
    bureaus = ['Kolkata Editorial Desk', 'New Delhi National Bureau', 'Mumbai Financial Wire', 'National Press Service', 'Regional Reporting Unit']
    
    safe_templates = [
        ("Comprehensive Review of Regional Infrastructure and Urban Transit Expansion", 
         "State municipal authorities release evaluation metrics highlighting accelerated execution timelines, transparent resource allocation, and stringent safety protocols across civic development works."),
        ("Financial Market Analysis Highlights Steady Performance Across Key Industrial Indices", 
         "Institutional brokerage summaries indicate positive investor sentiment driven by robust corporate earnings reports and consistent domestic liquidity management measures."),
        ("Digital Governance Initiatives Expand Access to Essential Public Services in Rural Districts", 
         "Administrative departments scale up high-speed optical fiber connectivity and digital kiosk networks, facilitating seamless certificate issuance and grievance redressal for citizens."),
        ("Environmental Protection Boards Enforce Standard Compliance for Industrial Units", 
         "Regional pollution control boards conduct comprehensive facility audits, mandating advanced effluent treatment installations and continuous emission tracking to protect ecological balance."),
        ("National Athletic Federation Outlines Structured Training Regimens for Upcoming International Events", 
         "Sports science experts collaborate with national coaches to implement advanced conditioning protocols, biometric performance monitoring, and tactical preparation camps for elite competitors.")
    ]

    base_time = datetime.now()
    all_articles = []
    
    for i in range(1200):
        tmpl = safe_templates[i % len(safe_templates)]
        cat = categories[i % len(categories)]
        bureau = bureaus[i % len(bureaus)]
        
        unique_title = f"{tmpl[0]} — Bulletin #{i+1}" if i > 5 else tmpl[0]
        summary_text = f"{bureau} — {tmpl[1]} Independent field correspondents confirm that official monitoring bodies are maintaining rigorous oversight to ensure complete adherence to regulatory standards and public accountability."

        pub_time = base_time - timedelta(minutes=i * 10)
        
        image_pool = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1000",
            "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1000",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000"
        ]

        item = {
            'id': str(9500 + i),
            'title': unique_title,
            'summary': summary_text,
            'category': cat,
            'link': f"/news/{9500 + i}",
            'image': image_pool[i % len(image_pool)],
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

    fresh_data = generate_safe_professional_news()
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
