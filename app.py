import os
import json
from flask import Flask, render_template, abort
from apscheduler.schedulers.background import BackgroundScheduler
from news_engine import fetch_and_generate

app = Flask(__name__)
DB_FILE = "data/news.json"

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