import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_ultra_seo_longform_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def generate_deep_seo_articles():
    categories = ['India', 'World', 'Business', 'Technology', 'Sports', 'Regional']
    bureaus = ['Kolkata Special Investigation Desk', 'New Delhi National Bureau', 'Mumbai Financial Intelligence Unit', 'Global Affairs Newsroom', 'Technology & Innovation Wire']
    
    # গুগলের এসইও ট্রেন্ডিং গাইডলাইন মেনে দীর্ঘ ও প্রফেশনাল আর্টিকেলের কাঠামো
    seo_templates = [
        ("Comprehensive National Infrastructure & Digital Transformation Roadmap for 2026", 
         "An in-depth investigative report analyzing the sweeping policy shifts, budgetary allocations, and technological integration driving regional and national development. Experts evaluate the long-term socioeconomic impact, employment generation metrics, and administrative transparency frameworks established by regulatory authorities."),
        ("Global Economic Resilience: Market Dynamics, Technological Innovation and Trade Strategies", 
         "A meticulous financial analysis reviewing macroeconomic indicators, multinational corporate earnings reports, supply chain optimizations, and monetary policy adjustments across major international exchanges amidst shifting geopolitical landscapes."),
        ("Next-Generation Artificial Intelligence Governance and Cybersecurity Frameworks", 
         "An extensive examination of emerging regulatory standards for secure cloud computing, data privacy compliance, enterprise automation protocols, and the ethical deployment of artificial intelligence across critical public and private sectors."),
        ("Sustainable Environmental Engineering and Renewable Energy Transition Strategies", 
         "A comprehensive overview of large-scale photovoltaic installations, decentralized smart grid deployments, zero-discharge industrial manufacturing norms, and international climate observation telemetry data aimed at achieving carbon neutrality goals."),
        ("Elite Athletic Training Methodologies and Sports Science Integration in International Championships", 
         "An exhaustive sports journalism feature detailing tactical conditioning camps, biometric performance analytics, nutritional science applications, and squad selections across national sports federations preparing for global tournaments.")
    ]

    base_time = datetime.now()
    all_articles = []
    
    # হাজার হাজার দীর্ঘ ফরম্যাট এসইও অপ্টিমাইজড খবর তৈরি
    for i in range(1800):
        tmpl = seo_templates[i % len(seo_templates)]
        cat = categories[i % len(categories)]
        bureau = bureaus[i % len(bureaus)]
        
        unique_title = f"{tmpl[0]} — Special Report Vol. {i+1}" if i > 5 else tmpl[0]
        
        # ৫০০০ শব্দের মধ্যে বিস্তারিত ও আকর্ষণীয় হিউম্যান জার্নালিজম স্টাইল বডি টেক্সট
        detailed_body = f"""
        {bureau} — In a rapidly evolving landscape, {tmpl[1]} 
        
        Detailed investigations and official press dispatches indicate that multi-sectoral committees are closely monitoring implementation milestones. Analysts point out that structural reforms, rigorous compliance protocols, and proactive stakeholder engagement remain the cornerstone of this initiative. 
        
        ### Background and Strategic Objectives
        The primary objective centers around establishing sustainable operational benchmarks while maximizing public accountability and economic efficiency. Over the past fiscal cycles, stakeholders have observed significant improvements in resource allocation, digital transparency, and technological adoption. Independent economic observers note that these proactive measures insulate domestic markets from external volatilities.
        
        ### Comprehensive Impact Assessment
        Industry leaders and policy makers have lauded the comprehensive approach adopted by the governing bodies. Key performance indicators suggest a measurable surge in productivity, enhanced consumer protection, and accelerated infrastructural execution. Furthermore, specialized working groups continue to evaluate feedback from grassroots entities to refine tactical execution.
        
        ### Future Outlook and Expert Perspectives
        As the roadmap unfolds into subsequent phases, international observers maintain an optimistic outlook. Continued investment in digital infrastructure, human capital development, and transparent governance is expected to yield compounding dividends well into the future. Editorial follow-ups will track real-time developments as official bodies release quarterly progress audits.
        """

        pub_time = base_time - timedelta(minutes=i * 8)
        
        image_gallery = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1200",
            "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1200",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200"
        ]

        item = {
            'id': str(9000 + i),
            'title': unique_title,
            'summary': detailed_body.strip(),
            'category': cat,
            'link': f"/news/{9000 + i}",
            'image': image_gallery[i % len(image_gallery)],
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

    fresh_data = generate_deep_seo_articles()
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
