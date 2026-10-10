from flask import Flask, render_template, request, jsonify
import feedparser
import re
from datetime import datetime

app = Flask(__name__)

# বিশ্বের প্রধান প্রধান অঞ্চলের আন্তর্জাতিক আরএসএস ফিডস
COUNTRY_FEEDS = {
    'IN': {'name': 'India', 'feed': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'},
    'BD': {'name': 'Bangladesh', 'feed': 'https://www.thedailystar.net/frontpage/rss.xml'},
    'US': {'name': 'United States', 'feed': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'},
    'UK': {'name': 'United Kingdom', 'feed': 'https://feeds.bbci.co.uk/news/uk/rss.xml'},
    'CA': {'name': 'Canada', 'feed': 'https://www.cbc.ca/cmlink/rss-topstories'},
    'AU': {'name': 'Australia', 'feed': 'https://www.abc.net.au/news/feed/51120/rss.xml'},
    'DE': {'name': 'Germany', 'feed': 'https://rss.dw.com/rdf/rss-en-all'},
    'FR': {'name': 'France', 'feed': 'https://www.france24.com/en/rss'},
    'JP': {'name': 'Japan', 'feed': 'https://www3.nhk.or.jp/nhkworld/en/news/tags/1/rss.xml'},
    'AE': {'name': 'Middle East / UAE', 'feed': 'https://www.aljazeera.com/xml/rss/all.xml'}
}

GLOBAL_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best'
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def fetch_all_news(country_code=None):
    news_items = []
    feeds_to_fetch = []

    if country_code and country_code.upper() in COUNTRY_FEEDS:
        feeds_to_fetch.append((country_code.upper(), COUNTRY_FEEDS[country_code.upper()]['feed'], COUNTRY_FEEDS[country_code.upper()]['name']))
    else:
        for c_code, meta in COUNTRY_FEEDS.items():
            feeds_to_fetch.append((c_code, meta['feed'], meta['name']))
        for g_feed in GLOBAL_FEEDS:
            feeds_to_fetch.append(('WORLD', g_feed, 'World'))

    idx = 1
    for c_code, feed_url, c_name in feeds_to_fetch:
        try:
            d = feedparser.parse(feed_url)
            for entry in d.entries[:6]:
                img = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800&auto=format&fit=crop&q=60"
                if 'media_content' in entry and len(entry.media_content) > 0:
                    img = entry.media_content[0].get('url', img)
                elif 'links' in entry:
                    for l in entry.links:
                        if l.get('type', '').startswith('image/'):
                            img = l.get('href', img)
                            break

                pub_date = entry.get('published', '')
                if not pub_date:
                    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

                news_items.append({
                    'id': idx,
                    'title': entry.get('title', 'Breaking Global News'),
                    'summary': clean_html(entry.get('summary', entry.get('description', 'Detailed international dispatches.'))),
                    'date': pub_date,
                    'category': c_name,
                    'country_code': c_code,
                    'image': img,
                    'link': entry.get('link', '#')
                })
                idx += 1
        except Exception:
            continue

    if not news_items:
        news_items.append({
            'id': 1,
            'title': 'Global Monitoring Active: Connecting to Real-time Wires',
            'summary': 'Live news system is receiving latest updates from world channels.',
            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'category': 'World',
            'country_code': 'ALL',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&auto=format&fit=crop&q=60',
            'link': '#'
        })
    return news_items

cached_news = fetch_all_news()

@app.route('/')
def home():
    selected_country = request.args.get('country', 'ALL').upper()
    if selected_country != 'ALL' and selected_country in COUNTRY_FEEDS:
        filtered = [n for n in cached_news if n['country_code'] == selected_country]
        if not filtered:
            filtered = fetch_all_news(selected_country)
    else:
        filtered = cached_news

    lead = filtered[0] if filtered else None
    return render_template('index.html', news_list=filtered, lead=lead, selected_country=selected_country, countries=COUNTRY_FEEDS)

@app.route('/category/<cat_name>')
def category(cat_name):
    cat_items = [n for n in cached_news if cat_name.lower() in n['category'].lower()]
    if not cat_items:
        cat_items = cached_news
    lead = cat_items[0] if cat_items else None
    return render_template('index.html', news_list=cat_items, lead=lead, selected_country='ALL', countries=COUNTRY_FEEDS)

@app.route('/news/<int:news_id>')
def single_news(news_id):
    article = next((n for n in cached_news if n['id'] == news_id), None)
    if not article:
        article = cached_news[0] if cached_news else {
            'id': news_id,
            'title': 'Headline in Dispatch',
            'summary': 'Full dispatch coverage loading.',
            'date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'category': 'General',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&auto=format&fit=crop&q=60'
        }
    return render_template('single.html', article=article)

@app.route('/sync-news')
def sync():
    global cached_news
    cached_news = fetch_all_news()
    return jsonify({'status': 'success', 'count': len(cached_news)})

@app.route('/api/latest-lead')
def api_lead():
    country = request.args.get('country', 'ALL').upper()
    if country != 'ALL' and country in COUNTRY_FEEDS:
        items = [n for n in cached_news if n['country_code'] == country]
    else:
        items = cached_news
    if items:
        import random
        chosen = random.choice(items[:10])
        return jsonify({'status': 'success', 'news': chosen})
    return jsonify({'status': 'empty'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)