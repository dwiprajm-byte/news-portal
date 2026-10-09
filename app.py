import os
import json
import feedparser
from flask import Flask, render_template, abort

app = Flask(__name__)
DATA_FILE = "data/news.json"

# বিশ্বের শীর্ষ ভাইরাল, ট্রেন্ডিং ও হাই-সিপিসি নিউজ ফিড
RSS_FEEDS = {
    "National": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "International": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "Business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "Entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en",
    "Sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "Science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en"
}

def load_news():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_news(news_list):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

def fetch_trending_news():
    existing_news = load_news()
    existing_titles = {item["title"] for item in existing_news}
    new_items = []
    current_id = len(existing_news) + 1

    for category, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
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
        combined = new_items + existing_news
        save_news(combined[:120])
        return combined[:120]
    return existing_news

@app.route("/")
def home():
    news = fetch_trending_news()
    lead = news[0] if news else None
    remaining = news[1:] if len(news) > 1 else []
    return render_template("index.html", lead=lead, news_list=remaining)

@app.route("/category/<cat_name>")
def category_view(cat_name):
    news = load_news()
    filtered = [n for n in news if n.get("category", "").lower() == cat_name.lower()]
    return render_template("category.html", category_name=cat_name.title(), news_list=filtered)

@app.route("/news/<int:news_id>")
def single_news(news_id):
    news = load_news()
    article = next((n for n in news if n["id"] == news_id), None)
    if not article:
        abort(404)
    related = [n for n in news if n["id"] != news_id][:4]
    return render_template("single.html", article=article, related=related)

# পলিসি ও লিগ্যাল রাউট
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