import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_unlimited_seo_wire_2026"

DATA_FILE = "articles_store.json"

def clean_news_title(raw_title):
    t = re.sub(r'\s*-[^-]+$', '', raw_title)
    t = re.sub(r'[^\w\s\u0980-\u09FF]', '', t).strip().lower()
    return t

def generate_bulk_seo_news():
    # হাজার হাজার খবরের ডাটাভাণ্ডার (এসইও ও হিউম্যান জার্নালিজম ফ্রেন্ডলি)
    categories = ['India', 'World', 'Business', 'Technology', 'Sports', 'Regional']
    locations = ['Kolkata', 'New Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Hyderabad', 'Kalyani', 'Barachampa', 'Bongaon']
    
    generated = []
    
    # বিভিন্ন ক্যাটাগরির প্রিমিয়াম কনটেন্ট টেমপ্লেট
    templates = [
        ("Major Policy Shift Announced by Regulatory Authorities to Boost Digital Sector Growth", 
         "Comprehensive framework reforms introduced to streamline enterprise compliance, safeguard consumer data privacy, and foster indigenous technological innovation across domestic markets."),
        ("Infrastructure Modernization Projects Witness Rapid Execution Across Urban Centers", 
         "State and municipal engineering divisions accelerate roadway, metro rail, and utility pipeline upgrades, aiming to reduce transit congestion and improve regional mobility."),
        ("Quarterly Financial Results Reflect Resilient Corporate Performance and Strong Demand", 
         "Leading banking, manufacturing, and retail enterprises report robust revenue growth, beating market consensus estimates and strengthening investor confidence worldwide."),
        ("National Research Institutes Unveil Breakthrough Innovations in Renewable Energy Systems", 
         "Scientists demonstrate next-generation photovoltaic efficiencies and high-capacity grid battery storage solutions, marking a milestone toward carbon neutrality targets."),
        ("International Sports Federations Finalize Squad Selections and Training Schedules", 
         "Athletic committees conduct rigorous conditioning camps, implementing sports science metrics and tactical drills ahead of upcoming continental championships."),
        ("Agricultural Extension Programs Promote Water-Efficient Micro-Irrigation Technologies", 
         "Agronomists conduct regional field workshops to train farming communities on automated drip irrigation and soil health card utilization for winter crop cycles.")
    ]

    base_time = datetime.now()
    
    # হাজার খানেক ইউনিক খবর তৈরি করার লুপ
    news_id_counter = 9000
    for i in range(1200):
        tmpl = templates[i % len(templates)]
        cat = categories[i % len(categories)]
        loc = locations[i % len(locations)]
        
        # ইউনিক ভ্যারিয়েশন তৈরি
        title_suffix = f" — Edition {i+1}" if i > 5 else ""
        full_title = f"{tmpl[0]}{title_suffix}"
        
        # প্রফেশনাল হিউম্যান রিপোর্টিং স্টাইল সামারি
        summary_text = f"{loc} Bureau — {tmpl[1]} Editorial field dispatches confirm that specialized committees are closely monitoring implementation milestones to ensure absolute transparency and operational compliance."

        pub_time = base_time - timedelta(minutes=i * 15)
        
        img_urls = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1000",
            "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1000",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1000",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000"
        ]

        item = {
            'id': str(news_id_counter + i),
            'title': full_title,
            'summary': summary_text,
            'category': cat,
            'link': f"/news/{news_id_counter + i}",
            'image': img_urls[i % len(img_urls)],
            'published': pub_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        generated.append(item)
        
    return generated

def get_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if isinstance(items, list) and len(items) > 10:
                    return items
        except Exception:
            pass

    # যদি ফাইল না থাকে তবে তাৎক্ষণিকভাবে ১২০০+ এসইও অপ্টিমাইজড খবর জেনারেট করে সেভ করা
    bulk_data = generate_bulk_seo_news()
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(bulk_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return bulk_data

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
