from flask import Flask, render_template, request
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)

# বিশ্বস্ত ও আসল সংবাদ সংস্থার RSS ফিড (পাইথনের বিল্ট-ইন লাইব্রেরি দিয়ে পার্স করা হবে)
RSS_FEEDS = {
    "India": "https://news.google.com/rss/search?q=India+news&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=World+news&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=Business+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=Technology+news&hl=en-IN&gl=IN&ceid=IN:en"
}

def get_live_news():
    news_items = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for category, url in RSS_FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                channel = root.find('channel')
                if channel is not None:
                    for item in channel.findall('item')[:5]:
                        title = item.find('title').text if item.find('title') is not None else 'Breaking News'
                        link = item.find('link').text if item.find('link') is not None else '#'
                        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.now().strftime('%d %b %Y')
                        
                        news_items.append({
                            "title": title,
                            "category": category,
                            "published": pubDate[:16],
                            "image": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80",
                            "summary": "Read full coverage of this latest breaking news dispatch from verified sources.",
                            "link": link
                        })
        except Exception as e:
            print(f"Error fetching {category}: {e}")
    
    # যদি কোনো কারণে নেটওয়ার্ক সমস্যা হয় তবে ব্যাকআপ প্রিমিয়াম খবর দেখাবে
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
