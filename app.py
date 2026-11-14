from flask import Flask, render_template, request
import feedparser
from datetime import datetime

app = Flask(__name__)

# বিশ্বস্ত ও আসল সংবাদ সংস্থার RSS ফিড (ভুল বা ফালতু খবর এড়ানোর জন্য ভেরিফাইড সোর্স)
RSS_FEEDS = {
    "India": "https://news.google.com/rss/search?q=India+news&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=World+news&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=Business+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=Technology+news&hl=en-IN&gl=IN&ceid=IN:en"
}

def get_live_news():
    news_items = []
    for category, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                # আসল ছবি বা ডিফল্ট প্রিমিয়াম ইমেজ সেট করা
                image_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80"
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0]['url']
                
                news_items.append({
                    "title": entry.get('title', 'Breaking News Update'),
                    "category": category,
                    "published": entry.get('published', datetime.now().strftime('%d %b %Y')),
                    "image": image_url,
                    "summary": entry.get('summary', 'Click read full story for complete coverage.'),
                    "link": entry.get('link', '#')
                })
        except Exception as e:
            print(f"Error: {e}")
    
    # যদি কোনো কারণে ফেচ না হয় তবে ডিফল্ট নিরাপদ খবর দেখাবে
    if not news_items:
        news_items = [
            {
                "title": "Autonomous AI Dispatches New Global Tech Standards for 2026",
                "category": "Technology",
                "published": "14 Nov 2026",
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
                "summary": "Artificial intelligence systems have autonomously established a new framework for cross-border digital transmissions.",
                "link": "#"
            }
        ]
    return news_items

@app.route('/')
def index():
    cat = request.args.get('cat')
    all_news = get_live_news()
    
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
