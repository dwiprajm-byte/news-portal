from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "24earlynews_rock_solid_key_2026"

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

    # ডিফল্ট নিশ্চিত খবর
    return [
        {
            'id': '101',
            'title': '24 Early News: Verified Global & Regional Media Network Live Wire',
            'summary': 'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting across national and international territories.',
            'category': 'India',
            'link': '/news/101',
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        },
        {
            'id': '102',
            'title': 'Global Economic Outlook: Technology and Market Trends for 2026',
            'summary': 'Market analysts review major industrial developments and digital media growth trends across Asian and global exchanges.',
            'category': 'Business',
            'link': '/news/102',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        },
        {
            'id': '103',
            'title': 'Digital Media and Ground Journalism: A Shift Toward Verified Wire Services',
            'summary': 'The demand for transparent, fact-checked editorial standards continues to rise as newsrooms implement strict verification protocols.',
            'category': 'Technology',
            'link': '/news/103',
            'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
    ]

@app.route('/')
def home():
    try:
        articles = get_articles()
        return render_template('index.html', news=articles, news_list=articles)
    except Exception as e:
        return f"CRITICAL RENDER ERROR: {str(e)}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        articles = get_articles()
        target = next((item for item in articles if str(item.get('id')) == str(article_id)), articles[0])
        return render_template('single.html', article=target)
    except Exception:
        return redirect(url_for('home'))

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            category = request.form.get('category', 'India').strip()
            location = request.form.get('location', 'Kolkata').strip()
            author = request.form.get('author', '').strip()
            founder_pin = request.form.get('founder_pin', '').strip()
            content = request.form.get('content', '').strip()
            img_url = request.form.get('image_url', '').strip()

            if not title or not content:
                return redirect(url_for('submit_news'))

            if author.strip().upper() == 'DWIPRAJ MALLICK' and founder_pin != "6203":
                return "Security Error: Invalid Founder Passcode.", 403

            new_id = str(int(datetime.now().timestamp() * 1000))
            if not img_url:
                img_url = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000'

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
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(all_news, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

            return redirect(f"/news/{new_id}")
        except Exception as e:
            return f"Submission Error: {str(e)}", 500

    return render_template('submit.html')

@app.route('/privacy')
@app.route('/privacy-policy')
def privacy_page():
    return render_template('privacy.html')

@app.route('/about')
@app.route('/about-us')
def about_page():
    return render_template('about.html')

@app.route('/contact')
@app.route('/contact-us')
def contact_page():
    return render_template('contact.html')

@app.route('/terms')
@app.route('/terms-of-service')
def terms_page():
    return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
