from flask import Flask, render_template, request, abort
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import re

app = Flask(__name__)

DB_FILE = "news_store.json"

# গুগল ট্রেন্ডিং ও রিয়েল-টাইম নিউজ ফেচ করার জন্য ক্যাটাগরি ফিড
RSS_FEEDS = {
    "India": [
        "https://news.google.com/rss/search?q=India+news+trending&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "World": [
        "https://news.google.com/rss/search?q=World+news+top+stories&hl=en-US&gl=US&ceid=US:en"
    ],
    "Business": [
        "https://news.google.com/rss/search?q=Business+economy+market+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Tech": [
        "https://news.google.com/rss/search?q=Technology+AI+gadgets+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Sports": [
        "https://news.google.com/rss/search?q=Sports+cricket+football+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Cricket": [
        "https://news.google.com/rss/search?q=Cricket+match+updates&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Entertainment": [
        "https://news.google.com/rss/search?q=Entertainment+Bollywood+movies&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Auto": [
        "https://news.google.com/rss/search?q=Automobile+cars+bikes+launch&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Cities": [
        "https://news.google.com/rss/search?q=Kolkata+Delhi+Mumbai+local+news&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Trending": [
        "https://news.google.com/rss/search?q=Trending+viral+news+today&hl=en-IN&gl=IN&ceid=IN:en"
    ],
    "Education": [
        "https://news.google.com/rss/search?q=Education+exams+results+jobs&hl=en-IN&gl=IN&ceid=IN:en"
    ]
}

def clean_news_text(text):
    if not text:
        return ""
    unwanted_names = ["News24", "NEWS24", "News 24", "NDTV", "Aaj Tak", "Zee News", "ABP Live", "News18", "The Indian Express"]
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
                        for idx, item in enumerate(channel.findall('item')):
                            raw_title = item.find('title').text if item.find('title') is not None else ''
                            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime('%d %b %Y')
                            
                            title = clean_news_text(raw_title)
                            if not title:
                                continue
                                
                            # ইউনিক আইডি তৈরি যাতে ওয়েবসাইটের ভেতরেই পেজ ওপেন হয়
                            slug = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())[:60].strip('-')
                            slug = f"{slug}-{abs(hash(title)) % 10000}"
                            internal_link = f"/news/{slug}"
                            
                            # আসল ও প্রাসঙ্গিক হাই-কোয়ালিটি ছবি এসইও ফ্রেন্ডলিভাবে যুক্ত করা
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

                            if internal_link not in existing_links:
                                full_content = f"""
                                সাম্প্রতিক গুগল ট্রেন্ডস এবং রিয়েল-টাইম বিশ্লেষণে দেখা গেছে যে, '{title}' বিষয়টি বর্তমানে দেশজুড়ে অত্যন্ত গুরুত্বের সাথে আলোচিত হচ্ছে। 
                                24 Early News নেটওয়ার্কের বিশেষ প্রতিনিধি দলের সংগ্রহ করা তথ্য অনুযায়ী, এই ঘটনার পেছনে একাধিক গুরুত্বপূর্ণ দিক রয়েছে যা সাধারণ মানুষের নজর কেড়েছে। 
                                বিশেষজ্ঞ মহールの মতে, বর্তমান পরিস্থিতির প্রেক্ষাপটে এই আপডেটটি অত্যন্ত তাৎপর্যপূর্ণ। 
                                নির্ভরযোগ্য সূত্র মারফত জানা গেছে যে, সংশ্লিষ্ট কর্তৃপক্ষ এ বিষয়ে নিবিড় নজরদারি বজায় রাখছে। 
                                আমাদের নিজস্ব এডিটোরাল প্যানেল এই বিষয়ে ধারাবাহিক আপডেট প্রদান করবে। পাঠকদের সুবিধার জন্য প্রতিটি নতুন তথ্য রিয়েল-টাইমে এখানে প্রকাশ করা হচ্ছে।
                                """
                                
                                news_item = {
                                    "slug": slug,
                                    "title": title,
                                    "category": category,
                                    "published": pubDate[:16],
                                    "image": img_url,
                                    "summary": f"বিশেষ প্রতিবেদন: {title} সম্পর্কিত সর্বশেষ আপডেট, বিশ্লেষণ এবং বিস্তারিত তথ্য জানুন 24 Early News-এ।",
                                    "content": full_content.strip(),
                                    "link": internal_link
                                }
                                existing_news.insert(0, news_item)
                                existing_links.add(internal_link)
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
                "slug": "sample-news",
                "title": "Autonomous AI Dispatches New Global Tech Standards for 2026",
                "category": "Tech",
                "published": "14 Nov 2026",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
                "summary": "Artificial intelligence systems have autonomously established a new framework.",
                "content": "Detailed overview of autonomous AI dispatches and global technological evolution standards.",
                "link": "/news/sample-news"
            }
        ]

    if cat:
        filtered = [n for n in all_news if cat.lower() in n['category'].lower() or n['category'].lower() in cat.lower()]
        if not filtered:
            filtered = all_news
    else:
        filtered = all_news

    return render_template('index.html', news=filtered)

@app.route('/news/<slug>')
def news_detail(slug):
    all_news = load_saved_news()
    article = next((n for n in all_news if n.get('slug') == slug), None)
    if not article:
        abort(404)
    return render_template('detail.html', article=article)

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
