import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response

app = Flask(__name__)
app.secret_key = "24earlynews_fresh_production_2026"

DATA_FILE = "articles_store.json"

def get_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if isinstance(items, list) and len(items) > 0:
                    return items
        except Exception:
            pass
    
    return [
        {
            'id': '24001',
            'title': 'AI-Powered Automated Newsroom Revolutionizes Global Journalism Standards',
            'summary': 'An in-depth look at how artificial intelligence algorithms and real-time data pipelines are transforming digital media publishing, ensuring rapid dispatches with absolute journalistic integrity.',
            'category': 'Technology',
            'link': '/news/24001',
            'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
    ]

@app.route('/')
def home():
    articles = get_articles()
    cat = request.args.get('cat')
    filtered = [a for a in articles if a.get('category') == cat] if cat else articles
    return render_template('index.html', news=filtered if filtered else articles, news_list=articles)

@app.route('/news/<article_id>')
def view_article(article_id):
    articles = get_articles()
    target = next((item for item in articles if str(item.get('id')) == str(article_id)), articles[0])
    related = [item for item in articles if str(item.get('id')) != str(article_id)][:3]
    return render_template('single.html', article=target, related_news=related)

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'India').strip()
        content = request.form.get('content', '').strip()
        img_url = request.form.get('image_url', '').strip() or 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200'

        if title and content:
            new_id = str(int(datetime.now().timestamp() * 1000))
            new_article = {
                'id': new_id,
                'title': title,
                'summary': content,
                'category': category,
                'link': f"/news/{new_id}",
                'image': img_url,
                'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
            all_news = get_articles()
            all_news.insert(0, new_article)
            os.makedirs("static/uploads", exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_news[:5000], f, ensure_ascii=False, indent=2)
            return redirect(f"/news/{new_id}")
    return render_template('submit.html')

@app.route('/sitemap.xml')
def sitemap():
    base_url = "https://24earlynews.com"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in ['', '/about', '/privacy', '/terms', '/contact', '/submit-news']:
        xml.append(f'  <url><loc>{base_url}{page}</loc></url>')
    for art in get_articles():
        xml.append(f'  <url><loc>{base_url}{art["link"]}</loc></url>')
    xml.append('</urlset>')
    return Response("\n".join(xml), mimetype='application/xml')

@app.route('/privacy')
def privacy(): return render_template('privacy.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/terms')
def terms(): return render_template('terms.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
