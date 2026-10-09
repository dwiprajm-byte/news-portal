import os
import json
import time
import feedparser
from flask import Flask, render_template, abort

app = Flask(__name__)
DATA_FILE = "data/news.json"

# গ্লোবাল মেমোরি ক্যাশ (যাতে প্রতি ক্লিকে ফাইল রিড বা নেটওয়ার্ক রিকোয়েস্ট না হয়)
CACHED_NEWS = []
NEWS_DICT = {}
LAST_FETCH_TIME = 0
CACHE_DURATION = 600  # ১০ মিনিট পর পর ব্যাকগ্রাউন্ডে নতুন খবর খুঁজবে

RSS_FEEDS = {
    "National": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "International": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "Entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en",
    "Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en"
}

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
    
    # ক্যাশ ভ্যালিড থাকলে ইন্টারনেট থেকে ডাউনলোড করে ইউজারকে আটকে রাখবে না
    if not force and CACHED_NEWS and (now - LAST_FETCH_TIME < CACHE_DURATION):
        return CACHED_NEWS

    LAST_FETCH_TIME = now
    existing_titles = {item["title"] for item in CACHED_NEWS}
    new_items = []
    current_id = max([item["id"] for item in CACHED_NEWS], default=0) + 1

    for category, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                if entry.title not in existing_titles:
                    image_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800"
                    if "media_content" in entry and len(entry.media_content) > 0:
                        image_url = entry.media_content[0].get("url", image_url)
                    elif category == "Business":
                        image_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800"
                    elif category == "Entertainment":
                        image_url = "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800"
                    elif category == "Technology":
                        image_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"
                    elif category == "Sports":
                        image_url = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800"

                    summary = getattr(entry, "summary", entry.title)
                    new_items.append({
                        "id": current_id,
                        "title": entry.title,
                        "category": category,
                        "date": getattr(entry, "published", "Just Now"),
                        "image": image_url,
                        "content": summary
                    })
                    existing_titles.add(entry.title)
                    current_id += 1
        except Exception:
            continue

    if new_items:
        CACHED_NEWS = (new_items + CACHED_NEWS)[:150]
        NEWS_DICT = {item["id"]: item for item in CACHED_NEWS}
        save_to_disk()
        
    return CACHED_NEWS

# সার্ভার স্টার্ট হওয়ার সাথে সাথে মেমোরিতে খবর লোড করা
load_from_disk()
if not CACHED_NEWS:
    sync_trending_news(force=True)

@app.route("/")
def home():
    news = sync_trending_news()
    lead = news[0] if news else None
    remaining = news[1:] if len(news) > 1 else []
    return render_template("index.html", lead=lead, news_list=remaining)

# সুপার-ফাস্ট ইনস্ট্যান্ট সিঙ্গেল নিউজ রাউট (০.১ সেকেন্ডে ওপেন হবে)
@app.route("/news/<int:news_id>")
def single_news(news_id):
    article = NEWS_DICT.get(news_id)
    if not article:
        # মেমোরিতে না পেলে একবার ডিস্ক থেকে রিফ্রেশ
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