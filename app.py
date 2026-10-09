import os
import json
from flask import Flask, render_template, abort
from apscheduler.schedulers.background import BackgroundScheduler
from news_engine import fetch_and_generate

# ডিরেক্টরি পাথ স্বয়ংক্রিয়ভাবে নিশ্চিত করা
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_FILE = os.path.join(BASE_DIR, "data", "news.json")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_generate, trigger="interval", minutes=30)
scheduler.start()

def load_news():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.route("/")
def home():
    news_list = load_news()
    lead = news_list[0] if news_list else None
    rest = news_list[1:] if len(news_list) > 1 else []
    return render_template("index.html", lead=lead, news_list=rest)

@app.route("/news/<int:news_id>")
def single_news(news_id):
    news_list = load_news()
    article = next((item for item in news_list if item["id"] == news_id), None)
    if not article:
        abort(404)
    return render_template("single.html", article=article, trending=news_list[:5])

if __name__ == "__main__":
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) <= 2:
        fetch_and_generate()
    app.run(host="0.0.0.0", port=5000, debug=True)
