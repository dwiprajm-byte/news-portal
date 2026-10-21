import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_strict_seo_standard_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def generate_strict_seo_articles():
    categories = ['India', 'World', 'Business', 'Technology', 'Sports', 'Regional']
    bureaus = ['Kolkata Bureau', 'New Delhi Desk', 'Mumbai Financial Wire', 'National Press Service', 'Editorial Investigation Wing']
    
    # গুগলের ৯টি এসইও ধাপ (Title, Dateline, Lead Paragraph, Sub-headings, Long-form) মেনে তৈরি টেমপ্লেট
    seo_standards = [
        ("Comprehensive Analysis of National Infrastructure, Digital Growth and Policy Reforms", 
         "An investigative overview examining sweeping economic adjustments, technological integration, and civic development milestones designed to optimize regional productivity and public transparency."),
        ("Global Economic Trends: Market Resilience, Corporate Earnings and Trade Dynamics", 
         "A meticulous financial report reviewing macroeconomic indicators, multinational corporate performance, supply chain efficiencies, and monetary policy adjustments across international exchanges."),
        ("Next-Generation Artificial Intelligence Governance and Cybersecurity Compliance Frameworks", 
         "An extensive examination of emerging regulatory standards for secure cloud computing, data privacy protocols, enterprise automation, and ethical deployment across critical sectors."),
        ("Sustainable Environmental Engineering and Renewable Energy Transition Strategies", 
         "A detailed report outlining large-scale photovoltaic installations, decentralized smart grid deployments, zero-discharge manufacturing norms, and climate telemetry data analysis."),
        ("Elite Athletic Training Methodologies and Sports Science Integration in Major Championships", 
         "An exhaustive sports journalism feature detailing tactical conditioning camps, biometric performance analytics, nutritional science applications, and squad selections across national federations.")
    ]

    base_time = datetime.now()
    all_articles = []
    
    for i in range(1500):
        tmpl = seo_standards[i % len(seo_standards)]
        cat = categories[i % len(categories)]
        bureau = bureaus[i % len(bureaus)]
        
        # ১. এসইও ফ্রেন্ডলি আকর্ষণীয় শিরোনাম
        seo_title = f"{tmpl[0]} — Update #{i+1}" if i > 5 else tmpl[0]
        
        # ৩, ৪, ৫, ৬ নম্বর ধাপ মেনে হিউম্যান জার্নালিজম ও সাব-হেডিংযুক্ত বিস্তারিত ফরম্যাট
        seo_body = f"""
        {bureau} — {tmpl[1]} Official field dispatches confirm that independent oversight committees are maintaining rigorous scrutiny to ensure absolute compliance with national benchmarks.

        ### Executive Summary and Core Objectives
        The primary focus centers around establishing sustainable operational frameworks while maximizing economic efficiency and public accountability. Over recent fiscal cycles, stakeholders have observed measurable improvements in resource allocation, digital transparency, and technological adoption.

        ### Strategic Implementation and Expert Perspectives
        Industry leaders and policy analysts have lauded the comprehensive approach adopted by governing bodies. Key performance indicators suggest a steady surge in productivity, enhanced consumer protection, and accelerated infrastructural execution. Specialized working groups continue to evaluate grassroots feedback to refine tactical deployment.

        ### Future Outlook and Market Implications
        As the development roadmap unfolds into subsequent phases, international observers maintain an optimistic outlook. Continued investment in digital infrastructure, human capital development, and transparent governance is expected to yield compounding dividends across regional and national sectors.
        """

        pub_time = base_time - timedelta(minutes=i * 10)
        
        image_pool = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1200",
            "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1200",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200"
        ]

        item = {
            'id': str(10000 + i),
            'title': seo_title,
            'summary': seo_body.strip(),
            'category': cat,
            'link': f"/news/{10000 + i}",
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

    fresh_data = generate_strict_seo_articles()
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
