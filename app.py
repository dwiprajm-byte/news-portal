import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_robust_news_fix_2026"

DATA_FILE = "articles_store.json"

def generate_robust_articles():
    categories = ['Opinion', 'Analysis', 'Technology', 'Business', 'World', 'India']
    bureaus = ['Global Editorial Desk', 'Strategic Analysis Wire', 'Digital Policy Bureau', 'Market Intelligence Unit']
    
    category_images = {
        'Opinion': ["https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200", "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200"],
        'Analysis': ["https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=1200", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200"],
        'Technology': ["https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200"],
        'Business': ["https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200"],
        'World': ["https://images.unsplash.com/photo-1529101091764-c3526daf38fe?w=1200", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200"],
        'India': ["https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1200", "https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1200"]
    }

    templates = [
        ("Comprehensive Analysis of National Infrastructure, Digital Growth and Policy Reforms", 
         "An investigative overview examining sweeping economic adjustments, technological integration, and civic development milestones designed to optimize regional productivity and public transparency."),
        ("Global Economic Trends: Market Resilience, Corporate Earnings and Trade Dynamics", 
         "A meticulous financial report reviewing macroeconomic indicators, multinational corporate performance, supply chain efficiencies, and monetary policy adjustments across international exchanges."),
        ("Next-Generation Artificial Intelligence Governance and Cybersecurity Compliance Frameworks", 
         "An extensive examination of emerging regulatory standards for secure cloud computing, data privacy protocols, enterprise automation, and ethical deployment across critical sectors."),
        ("Strategic Shifts in Regional Commerce and Small-Scale Enterprise Financing", 
         "Evaluating the structural impact of modern liquidity frameworks, digital lending models, and consumer credit availability on emerging commercial ecosystems.")
    ]

    base_time = datetime.now()
    all_articles = []
    
    for i in range(150):
        tmpl = templates[i % len(templates)]
        cat = categories[i % len(categories)]
        bureau = bureaus[i % len(bureaus)]
        
        title = f"{tmpl[0]} — Report Vol. {i+1}" if i > 5 else tmpl[0]
        body = f"{bureau} — {tmpl[1]} Official field dispatches confirm that independent oversight committees are maintaining rigorous scrutiny to ensure absolute compliance with national benchmarks."

        pub_time = base_time - timedelta(minutes=i * 15)
        pool = category_images.get(cat, category_images['Opinion'])
        img = pool[i % len(pool)]

        item = {
            'id': str(18000 + i),
            'title': title,
            'summary': body,
            'category': cat,
            'link': f"/news/{18000 + i}",
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
                if isinstance(items, list) and len(items) > 5:
                    return items
        except Exception:
            pass

    fresh_data = generate_robust_articles()
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
            category = request.form.get('category', 'Opinion').strip()
            content = request.form.get('content', '').strip()
            img_url = request.form.get('image_url', '').strip()

            if not title or not content:
                return redirect(url_for('submit_news'))

            new_id = str(int(datetime.now().timestamp() * 1000))
            if not img_url:
                img_url = 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200'

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
