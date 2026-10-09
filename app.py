import os
import json
import time
import re
import urllib.parse
import feedparser
from bs4 import BeautifulSoup
from flask import Flask, render_template, abort, redirect, url_for

app = Flask(__name__)
DATA_FILE = "data/news.json"

CACHED_NEWS = []
NEWS_DICT = {}
LAST_FETCH_TIME = 0
CACHE_DURATION = 180

# আন্তর্জাতিক উন্মুক্ত ও পাবলিক ফিড
RSS_FEEDS = {
    "National": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    "International": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "Entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "Sports": "https://feeds.bbci.co.uk/sport/rss.xml"
}

# ক্যাটাগরি ভিত্তিক প্রিমিয়াম ও ১০০% কপিরাইট-মুক্ত হাই-ডেফিনিশন আসল প্রেস লাইব্রেরি
COPYRIGHT_FREE_FALLBACKS = {
    "National": [
        "https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=900&auto=format&fit=crop"
    ],
    "International": [
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&auto=format&fit=crop"
    ],
    "Business": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=900&auto=format&fit=crop"
    ],
    "Technology": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=900&auto=format&fit=crop"
    ],
    "Entertainment": [
        "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=900&auto=format&fit=crop"
    ],
    "Sports": [
        "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=900&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=900&auto=format&fit=crop"
    ]
}

def get_copyright_safe_image(entry, category, item_index):
    """কপিরাইট মুক্ত ও আসল প্রাসঙ্গিক ছবি নিশ্চিত করার নিরাপদ ফিল্টার"""
    # ১. আরএসএস মিডিয়া থাম্বনেইল চেক (পাবলিক ডোমেইন ফেয়ার-ইউজ এম্বেডিং)
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get("url")
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url")
    if "enclosures" in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")

    # ২. ডেসক্রিপশনের ভেতরের অরিজিনাল ইমেজ
    content_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
    if content_html:
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html, re.IGNORECASE)
        if img_match:
            return img_match.group(1)

    # ৩. শতভাগ রয়্যালটি-ফ্রি কিউরেটেড প্রেস ছবি
    fallback_pool = COPYRIGHT_FREE_FALLBACKS.get(category, COPYRIGHT_FREE_FALLBACKS["National"])
    return fallback_pool[item_index % len(fallback_pool)]

def load_from_disk():
    global CACHED_NEWS, NEWS_DICT
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                CACHED_NEWS = json.load(f)
                NEWS_DICT = {item["id"]: item for item in CACHED_NEWS}
        except Exception:
            CACHED_NEWS = []
            NEWS_DICT = {}

def save_to_disk():
    os.makedirs("data", exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(CACHED_NEWS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def sync_trending_news(force=False):
    global CACHED_NEWS, NEWS_DICT, LAST_FETCH_TIME
    now = time.time()
    
    if not force and CACHED_NEWS and (now - LAST_FETCH_TIME < CACHE_DURATION):
        return CACHED_NEWS

    LAST_FETCH_TIME = now
    existing_titles = {item["title"] for item in CACHED_NEWS}
    new_items = []
    current_id = max([item["id"] for item in CACHED_NEWS], default=0) + 1

    for category, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for idx, entry in enumerate(feed.entries[:6]):
                if entry.title not in existing_titles:
                    safe_image = get_copyright_safe_image(entry, category, idx)
                    raw_summary = getattr(entry, "summary", entry.title)
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()

                    new_items.append({
                        "id": current_id,
                        "title": entry.title,
                        "category": category,
                        "date": getattr(entry, "published", "Just Now"),
                        "image": safe_image,
                        "content": clean_summary
                    })
                    existing_titles.add(entry.title)
                    current_id += 1
        except Exception:
            continue

    if new_items:
        CACHED_NEWS = (new_items + CACHED_NEWS)[:160]
        NEWS_DICT = {item["id"]: item for item in CACHED_NEWS}
        save_to_disk()
        
    return CACHED_NEWS

load_from_disk()
if not CACHED_NEWS:
    sync_trending_news(force=True)

@app.route("/")
def home():
    news = sync_trending_news()
    lead = news[0] if news else None
    remaining = news[1:] if len(news) > 1 else []
    return render_template("index.html", lead=lead, news_list=remaining)

@app.route("/sync-news")
def force_sync():
    sync_trending_news(force=True)
    return redirect(url_for("home"))

@app.route("/news/<int:news_id>")
def single_news(news_id):
    article = NEWS_DICT.get(news_id)
    if not article:
        load_from_disk()
        article = NEWS_DICT.get(news_id)
        if not article:
            abort(404)
    related = [n for n in CACHED_NEWS if n["id"] != news_id][:4]
    return render_template("single.html", article=article, related=related)

@app.route("/category/<cat_name>")
def category_view(cat_name):
    filtered = [n for n in CACHED_NEWS if n.get("category", "").lower() == cat_name.lower()]
    return render_template("category.html", category_name=cat_name.title(), news_list=filtered)

@app.route("/privacy-policy")
def privacy_policy(): return render_template("privacy-policy.html")

@app.route("/terms")
def terms(): return render_template("terms.html")

@app.route("/disclaimer")
def disclaimer(): return render_template("disclaimer.html")

@app.route("/about")
def about(): return render_template("about.html")

@app.route("/contact")
def contact(): return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
@app.route('/horoscope')
def horoscope_view():
    return render_template('horoscope.html')

@app.route('/recipes')
def recipes_view():
    return render_template('recipes.html')