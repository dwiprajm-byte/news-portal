from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# ইন-মেমোরি নিউজ স্টোরেজ (ডেমো ডাটা)
news_list = [
    {
        "title": "Autonomous AI Dispatches New Global Tech Standards for 2026",
        "category": "Technology",
        "published": "14 Nov 2026",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "summary": "Artificial intelligence systems have autonomously established a new framework for cross-border digital transmissions, enhancing latency and encryption standards worldwide.",
        "link": "#"
    },
    {
        "title": "Economic Markets Rally Following Automated Trade Protocols",
        "category": "Business",
        "published": "14 Nov 2026",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80",
        "summary": "Global financial indexes experienced a notable surge today as automated regulatory compliance tools streamlined cross-continental investments.",
        "link": "#"
    },
    {
        "title": "New Infrastructure Initiatives Unveiled Across Major Urban Hubs",
        "category": "India",
        "published": "13 Nov 2026",
        "image": "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80",
        "summary": "Municipal authorities have greenlit advanced smart-transit corridors designed to drastically reduce congestion and carbon emissions.",
        "link": "#"
    },
    {
        "title": "Global Climate Summit Concludes With Breakthrough Agreements",
        "category": "World",
        "published": "13 Nov 2026",
        "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
        "summary": "Delegates from over 150 nations finalized a binding pact on shared renewable energy grids and automated carbon tracking.",
        "link": "#"
    }
]

@app.route('/')
def index():
    cat = request.args.get('cat')
    filtered_news = news_list
    if cat:
        filtered_news = [n for n in news_list if n['category'].lower() == cat.lower()]
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
