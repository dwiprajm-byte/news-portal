import os
import json
import feedparser
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")
if API_KEY and API_KEY != "your_api_key_here":
    genai.configure(api_key=API_KEY)

DB_FILE = "data/news.json"

FEEDS = {
    "National": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "International": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "Sports": "https://feeds.bbci.co.uk/sport/rss.xml",
    "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
}

def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text()

def fetch_and_generate():
    existing_news = []
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                existing_news = json.load(f)
        except Exception:
            existing_news = []

    existing_titles = {item.get("original_title") for item in existing_news}
    new_articles = []

    for category, url in FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            raw_title = entry.title
            if raw_title in existing_titles:
                continue

            summary = clean_html(entry.summary if "summary" in entry else entry.title)
            
            image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&auto=format&fit=crop&q=80"
            if "media_content" in entry and len(entry.media_content) > 0:
                image_url = entry.media_content[0].get("url")
            elif "links" in entry:
                for link in entry.links:
                    if link.get("type", "").startswith("image/"):
                        image_url = link.get("href")
                        break

            title = raw_title
            content = f"<p>{summary}</p>"

            if API_KEY and API_KEY != "your_api_key_here":
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"""
                    You are a senior news editor. Rewrite this into an SEO-optimized news report:
                    Original Title: {raw_title}
                    Summary: {summary}
                    
                    Format:
                    TITLE: Engaging Headline Here
                    CONTENT: <p>Detailed HTML body paragraphs</p>
                    """
                    res = model.generate_content(prompt).text
                    if "TITLE:" in res and "CONTENT:" in res:
                        parts = res.split("CONTENT:")
                        title = parts[0].replace("TITLE:", "").strip()
                        content = parts[1].strip()
                except Exception as e:
                    print("AI Processing Error:", e)

            article = {
                "id": len(existing_news) + len(new_articles) + 1,
                "original_title": raw_title,
                "title": title,
                "content": content,
                "category": category,
                "image": image_url,
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "views": "1.5k"
            }
            new_articles.append(article)

    if new_articles:
        combined = new_articles + existing_news
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(combined[:60], f, ensure_ascii=False, indent=2)
        print(f"Success: {len(new_articles)} new articles added.")
    else:
        print("No new updates found.")

if __name__ == "__main__":
    fetch_and_generate()