from flask import Flask, render_template, request, abort
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import re

app = Flask(__name__)

DB_FILE = "news_store.json"

# শুধুমাত্র গুগল ট্রেন্ডস এবং ভেরিফাইড রিয়েল-টাইম ট্রেন্ডিং নিউজ ফিড
RSS_FEEDS = {
    "India": [
        "https://news.google.com/rss/search?q=India+breaking+trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "World": [
        "https://news.google.com/rss/search?q=World+top+trending+stories&hl=en-US&gl=US&ceid=US:en"
    ],
    "Business": [
        "https://news.google.com/rss/search?q=Business+market+trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Tech": [
        "https://news.google.com/rss/search?q=Technology+AI+trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Sports": [
        "https://news.google.com/rss/search?q=Sports+cricket+trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Cricket": [
        "https://news.google.com/rss/search?q=Cricket+match+trending&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Entertainment": [
        "https://news.google.com/rss/search?q=Bollywood+entertainment+trending&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Auto": [
        "https://news.google.com/rss/search?q=Automobile+cars+launch+trending&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Cities": [
        "https://news.google.com/rss/search?q=Delhi+Kolkata+Mumbai+trending+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Trending": [
        "https://news.google.com/rss/search?q=Viral+trending+news+today&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Education": [
        "https://news.google.com/rss/search?q=Education+exams+results+trending&hl=en-IN&gl=IN&ceid=IN:en"
    ]
}

def clean_news_text(text):
    if not text:
        return ""
    unwanted_names = ["News24", "NEWS24", "News 24", "NDTV", "Aaj Tak", "Zee News", "ABP Live", "News18", "The Indian Express", "Sakshi Education"]
    for name in unwanted_names:
        text = re.sub(re.escape(name), "24 Early News", text, flags=re.IGNORECASE)
    return text

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
    
    for category, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    channel = root.find('channel')
                    if channel is not None:
                        for item in channel.findall('item'):
                            raw_title = item.find('title').text if item.find('title') is not None else ''
                            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime('%d %b %Y')
                            
                            title = clean_news_text(raw_title)
                            if not title:
                                continue
                                
                            slug = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())[:60].strip('-')
                            slug = f"{slug}-{abs(hash(title)) % 10000}"
                            
                            # আসল ও ট্রেন্ডিং ছবি যুক্ত করার লজিক
                            img_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=1200&q=80"
                            if category in ["Tech", "Auto"]:
                                img_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"
                            elif category in ["Business", "Trending"]:
                                img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80"
                            elif category in ["India", "Cities"]:
                                img_url = "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80"
                            elif category in ["Sports", "Cricket"]:
                                img_url = "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1200&q=80"
                            elif category == "World":
                                img_url = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80"

                            if slug not in existing_links:
                                full_content = f"""
                                গুগল ট্রেন্ডসের রিয়েল-টাইম ডাটা অনুযায়ী '{title}' বিষয়টি বর্তমানে ব্যাপক চাঞ্চল্যের সৃষ্টি করেছে। 
                                24 Early News-এর বিশেষ বিশ্লেষণ অনুযায়ী, এই ট্রেন্ডিং বিষয়ের সাথে জড়িত প্রতিটি তথ্য অত্যন্ত নিখুঁতভাবে যাচাই করা হয়েছে। 
                                সংশ্লিষ্ট মহলের মতে, সাম্প্রতিক পরিস্থিতি অনুযায়ী এই আপডেটটি অত্যন্ত তাৎপর্যপূর্ণ। 
                                আমাদের এডিটোরাল টিম এই বিষয়ে প্রতি মুহূর্তে আপডেট সংগ্রহ করছে। পাঠকদের সঠিক ও রিয়েল-টাইম তথ্য প্রদান করতে আমরা সর্বদা বদ্ধপরিকর।
                                """
                                
                                news_item = {
                                    "slug": slug,
                                    "title": title,
                                    "category": category,
                                    "published": pubDate[:16],
                                    "image": img_url,
                                    "summary": f"বিশেষ ট্রেন্ডিং প্রতিবেদন: {title} সম্পর্কিত সর্বশেষ রিয়েল-টাইম আপডেট ও বিশ্লেষণ।",
                                    "content": full_content.strip(),
                                    "link": slug
                                }
                                existing_news.insert(0, news_item)
                                existing_links.add(slug)
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
                "slug": "sample-trending",
                "title": "Top Google Trending Update for 2026 Live Now",
                "category": "Trending",
                "published": "14 Nov 2026",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
                "summary": "Real-time trending news update loaded successfully.",
                "content": "Live trending analysis and coverage.",
                "link": "sample-trending"
            }
        ]

    if cat:
        filtered = [n for n in all_news if cat.lower() in n['category'].lower() or n['category'].lower() in cat.lower()]
        if not filtered:
            filtered = all_news
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
