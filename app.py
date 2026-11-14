from flask import Flask, render_template, request, redirect, url_for
import feedparser
from datetime import datetime

app = Flask(__name__)

# বিশ্বস্ত নিউজ সোর্স ও RSS ফিড তালিকা (যেকথা থেকে অটোমেটিক খবর আপডেট হবে)
RSS_FEEDS = {
    "India": "https://news.google.com/rss/search?q=India+news&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=World+news&hl=en-US&gl=US&ceid=US:en",
    "Business": "https://news.google.com/rss/search?q=Business+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=Technology+news&hl=en-IN&gl=IN&ceid=IN:en"
}

def fetch_live_news():
    all_news = []
    for category, feed_url in RSS_FEEDS.items():
        try:
            parsed_feed = feedparser.parse(feed_url)
            for entry in parsed_feed.entries[:10]: # প্রতি ক্যাটাগরি থেকে ১০টি করে লেটেস্ট খবর নেওয়া হবে
                # ছবির লিংক বা ডিফল্ট ইমেজ সেট করা
                image_url = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80"
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'links' in entry:
                    for link in entry.links:
                        if 'type' in link and 'image' in link['type']:
                            image_url = link['href']

                news_item = {
                    "title": entry.get('title', 'No Title'),
                    "category": category,
                    "published": entry.get('published', datetime.now().strftime('%d %b %Y')),
                    "image": image_url,
                    "summary": entry.get('summary', 'Read the full dispatch on the source network.'),
                    "link": entry.get('link', '#')
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"Error fetching {category}: {e}")
    return all_news

@app.route('/')
def index():
    cat = request.args.get('cat')
    news_list = fetch_live_news()
    
    if cat:
        filtered_news = [n for n in news_list if n['category'].lower() == cat.lower()]
    else:
        filtered_news = news_list

    return render_template('index.html', news=filtered_news)

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
