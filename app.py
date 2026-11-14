from flask import Flask, render_template, request
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os

app = Flask(__name__)

# লোকাল ডাটা ফাইল যেখানে পুরনো খবরগুলো সংরক্ষিত থাকবে (যাতে পুরনো খবর মুছে না যায়)
DB_FILE = "news_store.json"

# দেশ, বিদেশ, রাজ্য ও স্থানীয় খবরের সুনির্দিষ্ট RSS ফিড (গুগল নিউজ ভেরিফাইড সোর্স)
RSS_FEEDS = {
    "India": "https://news.google.com/rss/search?q=India+news+OR+National+news&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=World+news+OR+Global+news&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=Business+news+Economy&hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=Technology+news+AI&hl=en-IN&gl=IN&ceid=IN:en",
    "Local": "https://news.google.com/rss/search?q=West+Bengal+news+Kolkata+local&hl=en-IN&gl=IN&ceid=IN:en"
}

def load_saved_news():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_news(news_list):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving DB: {e}")

def fetch_and_accumulate_news():
    existing_news = load_saved_news()
    existing_links = {n['link'] for n in existing_news}
    
    new_items_added = False
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for category, url in RSS_FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                channel = root.find('channel')
                if channel is not None:
                    for item in channel.findall('item'):
                        title = item.find('title').text if item.find('title') is not None else ''
                        link = item.find('link').text if item.find('link') is not None else ''
                        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime('%d %b %Y')
                        
                        if link and link not in existing_links:
                            # কপিরাইট মুক্ত নিরাপদ ও প্রাসঙ্গিক ছবি নির্বাচন
                            img_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80"
                            if "Technology" in category:
                                img_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
                            elif "Business" in category:
                                img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80"
                            elif "Local" in category:
                                img_url = "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80"

                            news_item = {
                                "title": title,
                                "category": category if category != "Local" else "India",
                                "published": pubDate[:16],
                                "image": img_url,
                                "summary": "Real-time verified dispatch covering local, national, and international developments.",
                                "link": link
                            }
                            existing_news.insert(0, news_item) # নতুন খবর উপরে যুক্ত হবে, পুরনো খবর মোছা হবে না
                            existing_links.add(link)
                            new_items_added = True
        except Exception as e:
            print(f"Error fetching {category}: {e}")
            
    if new_items_added or not existing_news:
        save_news(existing_news)
        
    return existing_news

@app.route('/')
def index():
    cat = request.args.get('cat')
    all_news = fetch_and_accumulate_news()
    
    if not all_news:
        all_news = [
            {
                "title": "Autonomous AI Dispatches New Global Tech Standards for 2026",
                "category": "Technology",
                "published": "14 Nov 2026",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
                "summary": "Artificial intelligence systems have autonomously established a new framework.",
                "link": "#"
            }
        ]

    if cat:
        filtered = [n for n in all_news if n['category'].lower() == cat.lower()]
    else:
        filtered = all_news

    return render_template('index.html', news=filtered)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
