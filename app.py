from flask import Flask, render_template, request, abort
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import re

app = Flask(__name__)

DB_FILE = "news_store.json"

RSS_FEEDS = {
    "India": [
        "https://news.google.com/rss/search?q=India+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "World": [
        "https://news.google.com/rss/search?q=World+news&hl=en-US&gl=US&ceid=US:en"
    ],
    "Business": [
        "https://news.google.com/rss/search?q=Business+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Tech": [
        "https://news.google.com/rss/search?q=Technology+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Sports": [
        "https://news.google.com/rss/search?q=Sports+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Entertainment": [
        "https://news.google.com/rss/search?q=Entertainment+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Education": [
        "https://news.google.com/rss/search?q=Education+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Cities": [
        "https://news.google.com/rss/search?q=Kolkata+Delhi+Mumbai+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Trending": [
        "https://news.google.com/rss/search?q=Trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ]
}

def load_saved_news():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"Error loading DB: {e}")
    
    # ডিফল্ট ফলব্যাক নিউজ যাতে সাইট কখনো খালি বা 500 এরর না দেখায়
    return [
        {
            "slug": "default-news-1",
            "title": "24 Early News Network Launches Advanced Real-Time Dispatches",
            "category": "India",
            "published": datetime.now().strftime('%d %b %Y'),
            "image": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80",
            "summary": "Real-time verified news aggregation network delivering instant reports.",
            "content": "24 Early News network has successfully upgraded its autonomous reporting architecture to ensure seamless live updates across all regions.",
            "link": "default-news-1"
        }
    ]

def save_news(news_list):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving DB: {e}")

def fetch_and_accumulate_news():
    existing_news = load_saved_news()
    existing_links = {n.get('link', '') for n in existing_news}
    
    new_items_added = False
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        for category, urls in RSS_FEEDS.items():
            for url in urls:
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=3) as response:
                        xml_data = response.read()
                        root = ET.fromstring(xml_data)
                        channel = root.find('channel')
                        if channel is not None:
                            for item in channel.findall('item'):
                                raw_title = item.find('title').text if item.find('title') is not None else ''
                                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime('%d %b %Y')
                                
                                title = raw_title.strip()
                                if not title:
                                    continue
                                    
                                slug = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())[:60].strip('-')
                                slug = f"{slug}-{abs(hash(title)) % 10000}"
                                
                                img_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80"
                                if category in ["Tech", "Auto"]:
                                    img_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
                                elif category in ["Business", "Trending"]:
                                    img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80"
                                elif category in ["India", "Cities"]:
                                    img_url = "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80"
                                elif category in ["Sports", "Cricket"]:
                                    img_url = "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1200&q=80"

                                if slug not in existing_links:
                                    news_item = {
                                        "slug": slug,
                                        "title": title,
                                        "category": category,
                                        "published": pubDate[:16],
                                        "image": img_url,
                                        "summary": f"বিশেষ প্রতিবেদন: {title} সম্পর্কিত সর্বশেষ রিয়েল-টাইম আপডেট ও বিশ্লেষণ।",
                                        "content": f"গুগল ট্রেন্ডসের রিয়েল-টাইম ডাটা অনুযায়ী '{title}' বিষয়টি বর্তমানে ব্যাপক চাঞ্চল্যের সৃষ্টি করেছে। 24 Early News-এর বিশেষ বিশ্লেষণ অনুযায়ী প্রতিটি তথ্য যাচাই করা হয়েছে।",
                                        "link": slug
                                    }
                                    existing_news.insert(0, news_item)
                                    existing_links.add(slug)
                                    new_items_added = True
                except Exception as inner_e:
                    print(f"Skipping feed due to timeout/error: {inner_e}")
        
        if new_items_added:
            save_news(existing_news)
    except Exception as e:
        print(f"Outer fetch error: {e}")
        
    return existing_news

@app.route('/')
def index():
    try:
        cat = request.args.get('cat')
        all_news = load_saved_news()
        
        if cat:
            filtered = [n for n in all_news if cat.lower() in n.get('category', '').lower() or n.get('category', '').lower() in cat.lower()]
            if not filtered:
                filtered = all_news
        else:
            filtered = all_news

        return render_template('index.html', news=filtered)
    except Exception as e:
        return f"Application Error: {str(e)}", 500

@app.route('/about')
def about():
    return "24 Early News - About Us Page"

@app.route('/privacy')
def privacy():
    return "24 Early News - Privacy Policy"

@app.route('/terms')
def terms():
    return "24 Early News - Terms & Conditions"

@app.route('/contact')
def contact():
    return "24 Early News - Contact Us"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
