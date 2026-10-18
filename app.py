from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime

app = Flask(__name__)
app.secret_key = "absolute_safe_key_2026"

# ইন-মেমরি ডেমো নিউজ ডাটাবেস (কোনো ফাইল ক্র্যাশের ঝুঁকি নেই)
GLOBAL_NEWS = [
    {
        'id': '101',
        'title': '24 Early News: Verified Global & Regional Media Network Live Wire',
        'summary': 'Kolkata — 24 Early News launches dedicated round-the-clock news wire dispatches ensuring ethical, verified, and ground-level reporting across national and international territories.',
        'category': 'India',
        'link': '/news/101',
        'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
        'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    }
]

@app.route('/')
def home():
    try:
        return render_template('index.html', news=GLOBAL_NEWS, news_list=GLOBAL_NEWS)
    except Exception as e:
        return f"Template Rendering Error: {str(e)}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        target = next((item for item in GLOBAL_NEWS if str(item.get('id')) == str(article_id)), GLOBAL_NEWS[0])
        return render_template('single.html', article=target)
    except Exception:
        return redirect(url_for('home'))

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'India').strip()
        location = request.form.get('location', 'Kolkata').strip()
        author = request.form.get('author', '').strip()
        founder_pin = request.form.get('founder_pin', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            return redirect(url_for('submit_news'))

        if author.strip().upper() == 'DWIPRAJ MALLICK' and founder_pin != "6203":
            return "Security Error: Invalid Founder Passcode.", 403

        new_id = str(int(datetime.now().timestamp() * 1000))
        new_obj = {
            'id': new_id,
            'title': title,
            'summary': content,
            'category': category,
            'link': f"/news/{new_id}",
            'image': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1000',
            'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        }
        GLOBAL_NEWS.insert(0, new_obj)
        return redirect(f"/news/{new_id}")

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
