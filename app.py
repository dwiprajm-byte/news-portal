import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.secret_key = "24earlynews_auto_breaking_2026"

DATA_FILE = "articles_store.json"

def generate_auto_breaking_news():
    categories = ['Opinion', 'Analysis', 'Technology', 'Business', 'World', 'India']
    titles = [
        "Breaking Analysis: Emerging Economic Shifts and Market Volatility Trends",
        "Live Update: Strategic Policy Adjustments in Global Digital Infrastructure",
        "Urgent Dispatch: Next-Gen Technology Integration and Regulatory Compliance",
        "Market Flash: Corporate Earnings and International Trade Framework Developments"
    ]
    summaries = [
        "Real-time updates confirm that independent oversight committees are closely monitoring evolving sector dynamics to ensure absolute transparency and compliance.",
        "Live field reports indicate substantial structural updates across major metropolitan exchange networks, signaling increased momentum.",
        "Continuous automated bulletins highlight critical milestones in cross-border technological deployment and public governance frameworks."
    ]
    
    base_time = datetime.now()
    all_articles = []
    
    # Keep existing articles if available, or generate fresh set
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                all_articles = json.load(f)
        except Exception:
            pass

    # Automatically inject a fresh breaking update if last update was over 60 seconds ago
    if not all_articles or (base_time - datetime.strptime(all_articles[0].get('published', base_time.strftime("%a, %d %b %Y %H:%M:%S GMT")), "%a, %d %b %Y %H:%M:%S GMT")).total_seconds() > 50:
        new_id = str(int(base_time.timestamp() * 1000))
        idx = int(base_time.timestamp()) % len(titles)
        new_item = {
            'id': new_id,
            'title': f"[LIVE BREAKING] {titles[idx]} — {base_time.strftime('%H:%M:%S')}",
            'summary': summaries[idx % len(summaries)],
            'category': categories[idx % len(categories)],
            'link': f"/news/{new_id}",
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200',
            'published': base_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        all_articles.insert(0, new_item)
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_articles[:5000], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    return all_articles

@app.route('/')
def home():
    try:
        articles = generate_auto_breaking_news()
        return render_template('index.html', news=articles, news_list=articles)
    except Exception as e:
        return f"CRITICAL RENDER ERROR: {str(e)}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        articles = generate_auto_breaking_news()
        target = next((item for item in articles if str(item.get('id')) == str(article_id)), articles[0])
        return render_template('single.html', article=target)
    except Exception:
        return redirect(url_for('home'))

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            category = request.form.get('category', 'Opinion').strip()
            content = request.form.get('content', '').strip()
            img_url = request.form.get('image_url', '').strip()

            if not title or not content:
                return redirect(url_for('submit_news'))

            new_id = str(int(datetime.now().timestamp() * 1000))
            if not img_url:
                img_url = 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200'

            new_article = {
                'id': new_id,
                'title': title,
                'summary': content,
                'category': category,
                'link': f"/news/{new_id}",
                'image': img_url,
                'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }

            all_news = generate_auto_breaking_news()
            all_news.insert(0, new_article)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_news[:5000], f, ensure_ascii=False, indent=2)

            return redirect(f"/news/{new_id}")
        except Exception as e:
            return f"Submission Error: {str(e)}", 500

    return render_template('submit.html')

@app.route('/privacy')
def privacy_page(): return render_template('privacy.html')

@app.route('/about')
def about_page(): return render_template('about.html')

@app.route('/contact')
def contact_page(): return render_template('contact.html')

@app.route('/terms')
def terms_page(): return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt(): return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
