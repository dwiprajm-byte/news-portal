import os
import json
import time
import re
import random
import datetime
import feedparser
from bs4 import BeautifulSoup
from flask import Flask, render_template, abort, redirect, url_for, request

app = Flask(__name__)
DATA_FILE = "data/news.json"

CACHED_NEWS = []
NEWS_DICT = {}
LAST_FETCH_TIME = 0
CACHE_DURATION = 180

RSS_FEEDS = {
    "National": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    "International": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "Entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "Sports": "https://feeds.bbci.co.uk/sport/rss.xml",
    "Science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
}

COPYRIGHT_FREE_FALLBACKS = {
    "National": ["https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=900", "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=900"],
    "International": ["https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=900", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900"],
    "Business": ["https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900", "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=900"],
    "Technology": ["https://images.unsplash.com/photo-1518770660439-4636190af475?w=900", "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=900"],
    "Entertainment": ["https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=900", "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=900"],
    "Sports": ["https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=900", "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=900"],
    "Science": ["https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900", "https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=900"]
}

def get_copyright_safe_image(entry, category, item_index):
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get("url")
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url")
    if "enclosures" in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")
    content_html = getattr(entry, "summary", "") or getattr(entry, "description", "")
    if content_html:
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html, re.IGNORECASE)
        if img_match:
            return img_match.group(1)
    fallback_pool = COPYRIGHT_FREE_FALLBACKS.get(category, COPYRIGHT_FREE_FALLBACKS["National"])
    return fallback_pool[item_index % len(fallback_pool)]

def load_from_disk():
    global CACHED_NEWS, NEWS_DICT
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                CACHED_NEWS = json.load(f)
                NEWS_DICT = {item["id"]: item for item in CACHED_NEWS}
        except Exception:
            CACHED_NEWS = []
            NEWS_DICT = {}

def save_to_disk():
    os.makedirs("data", exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(CACHED_NEWS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def sync_trending_news(force=False):
    global CACHED_NEWS, NEWS_DICT, LAST_FETCH_TIME
    now = time.time()
    if not force and CACHED_NEWS and (now - LAST_FETCH_TIME < CACHE_DURATION):
        return CACHED_NEWS

    LAST_FETCH_TIME = now
    existing_titles = {item["title"] for item in CACHED_NEWS}
    new_items = []
    current_id = max([item["id"] for item in CACHED_NEWS], default=0) + 1

    for category, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for idx, entry in enumerate(feed.entries[:6]):
                if entry.title not in existing_titles:
                    safe_image = get_copyright_safe_image(entry, category, idx)
                    raw_summary = getattr(entry, "summary", entry.title)
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()

                    new_items.append({
                        "id": current_id,
                        "title": entry.title,
                        "category": category,
                        "date": getattr(entry, "published", "Just Now"),
                        "image": safe_image,
                        "content": clean_summary
                    })
                    existing_titles.add(entry.title)
                    current_id += 1
        except Exception:
            continue

    if new_items:
        CACHED_NEWS = (new_items + CACHED_NEWS)[:180]
        NEWS_DICT = {item["id"]: item for item in CACHED_NEWS}
        save_to_disk()
        
    return CACHED_NEWS

load_from_disk()
if not CACHED_NEWS:
    sync_trending_news(force=True)

# --- প্রতিদিনের ৫০টি সম্পূর্ণ নতুন ডায়নামিক রেসিপি ইঞ্জিন ---
RECIPE_BASE_POOL = [
    {"name": "Traditional Kolkata Mutton Biryani", "meal": "Dinner", "time": "60 Mins", "cal": "580 kcal", "img": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800", "ing": "Mutton 500g, Basmati rice, Saffron milk, Ghee, Fried potatoes, Shahi garam masala.", "met": "Marinate meat with yogurt and spices. Half cook rice with whole spices. Layer meat, fried potatoes, and rice. Seal with dough and slow cook on dum for 45 minutes."},
    {"name": "Crispy South Indian Masala Dosa", "meal": "Breakfast", "time": "20 Mins", "cal": "220 kcal", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800", "ing": "Fermented dosa batter, Boiled potatoes, Mustard seeds, Curry leaves, Turmeric.", "met": "Spread batter thinly on hot greased tawa. Fill spiced potato mash in center, roll tightly and serve with sambar & coconut chutney."},
    {"name": "Restaurant Style Butter Chicken", "meal": "Dinner", "time": "40 Mins", "cal": "490 kcal", "img": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800", "ing": "Chicken boneless 500g, Tomatoes, Butter, Cream, Kasuri methi, Ginger-garlic.", "met": "Roast marinated chicken in butter. Simmer silky pureed tomato gravy with spices. Stir in cooked chicken and cream."},
    {"name": "Steamed Bengali Ilish Macher Bhapa", "meal": "Lunch", "time": "25 Mins", "cal": "340 kcal", "img": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800", "ing": "Hilsa fish 4 pcs, Mustard paste, Green chillies, Mustard oil, Turmeric, Salt.", "met": "Coat fish in mustard paste, green chillies and mustard oil. Steam in an airtight container for 15 minutes."},
    {"name": "Authentic Hyderabadi Chicken Dum Biryani", "meal": "Lunch", "time": "50 Mins", "cal": "520 kcal", "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800", "ing": "Chicken 500g, Aged Basmati, Mint, Fried onions, Whole spices, Yogurt, Saffron.", "met": "Marinate chicken in spiced curd. Layer fragrant rice, sprinkle mint and saffron. Cook sealed on dum."},
    {"name": "Creamy Shahi Paneer", "meal": "Dinner", "time": "30 Mins", "cal": "380 kcal", "img": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800", "ing": "Paneer cubes 250g, Cashew paste, Onions, Tomatoes, Cream, Cardamom powder.", "met": "Saute aromatics and blend with cashew paste for royal velvet gravy. Gently simmer paneer cubes for 6 minutes."},
    {"name": "Crispy Kolkata Street Style Egg Roll", "meal": "Snacks", "time": "15 Mins", "cal": "310 kcal", "img": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=800", "ing": "Paratha, 2 Eggs, Shredded cucumber & onions, Green chillies, Chaat masala, Kasundi.", "met": "Cook paratha on tawa with whisked eggs. Top with onion-cucumber salad, lemon juice and roll tightly."},
    {"name": "Healthy Oatmeal Breakfast Porridge", "meal": "Breakfast", "time": "10 Mins", "cal": "190 kcal", "img": "https://images.unsplash.com/photo-1584776296944-ab6fb57b0bdd?w=800", "ing": "Rolled oats 50g, Warm milk, Honey, Chia seeds, Fresh strawberries, Almond flakes.", "met": "Simmer oats in warm milk for 5 minutes. Pour into bowl, drizzle pure raw honey, and top with berries."},
    {"name": "Spicy Amritsari Chole Bhature", "meal": "Lunch", "time": "40 Mins", "cal": "550 kcal", "img": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?w=800", "ing": "Kabuli chana, Tea bag, Anardana powder, Chole masala, Maida, Yogurt.", "met": "Boil soaked chana with tea bag. Simmer in spicy dark tangy gravy. Deep fry puffy golden bhaturas."},
    {"name": "Quick Vegetable Hakka Noodles", "meal": "Snacks", "time": "15 Mins", "cal": "290 kcal", "img": "https://images.unsplash.com/photo-1612927601601-6638404737ce?w=800", "ing": "Noodles, Shredded cabbage, Bell peppers, Spring onions, Soy sauce, Vinegar.", "met": "Stir-fry shredded veggies on high heat in a wok. Toss noodles, soy sauce and seasonings for 2 minutes."},
    {"name": "Bengali Kosha Mangsho", "meal": "Lunch", "time": "55 Mins", "cal": "510 kcal", "img": "https://images.unsplash.com/photo-1545247181-516773cae754?w=800", "ing": "Mutton, Mustard oil, Fried onions, Curd, Whole garam masala.", "met": "Slow bhuna (kosha) mutton with ginger-garlic in mustard oil until dark mahogany glaze appears and oil separates."},
    {"name": "Fluffy Poori with Aloo Dum", "meal": "Breakfast", "time": "25 Mins", "cal": "360 kcal", "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800", "ing": "Wheat flour, Baby potatoes, Hing, Tomato puree, Cumin seeds.", "met": "Cook fried baby potatoes in spiced tomato-hing gravy. Roll and fry hot puffed pooris until golden."},
    {"name": "Classic Italian Margherita Pizza", "meal": "Dinner", "time": "30 Mins", "cal": "420 kcal", "img": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800", "ing": "Pizza crust, Plum tomato sauce, Mozzarella cheese, Fresh basil, Olive oil.", "met": "Spread savory tomato sauce across dough. Layer mozzarella and fresh basil leaves. Bake at 220°C for 10 minutes."},
    {"name": "High Protein Moong Dal Chilla", "meal": "Breakfast", "time": "15 Mins", "cal": "180 kcal", "img": "https://images.unsplash.com/photo-1626074353765-517a681e40be?w=800", "ing": "Moong dal paste, Paneer, Coriander, Ginger, Green chillies, Ghee.", "met": "Pour savory moong batter on pan. Stuff with crumbled paneer and fresh herbs. Cook until crisp on both sides."},
    {"name": "Creamy Italian Penne Alfredo", "meal": "Dinner", "time": "20 Mins", "cal": "460 kcal", "img": "https://images.unsplash.com/photo-1621996346565-e3d5d62810ef?w=800", "ing": "Penne pasta, Fresh garlic, Butter, Cream, Parmesan cheese, Black pepper.", "met": "Boil pasta al dente. In a saucepan melt butter, saute minced garlic, pour cream and toss pasta evenly in cheese sauce."},
    {"name": "Crispy Onion Pakoda & Masala Chai", "meal": "Snacks", "time": "15 Mins", "cal": "240 kcal", "img": "https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?w=800", "ing": "Sliced onions, Besan, Ajwain, Green chillies, Rice flour, Mustard oil.", "met": "Mix thinly sliced onions with spices and gram flour. Deep-fry small spoonfuls till golden brown and crunchy."},
    {"name": "Authentic Pav Bhaji", "meal": "Dinner", "time": "35 Mins", "cal": "430 kcal", "img": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800", "ing": "Mashed vegetables, Pav bhaji masala, Tomatoes, Butter, Soft pav buns.", "met": "Cook veggies with special masala on tawa with generous butter. Toast soft butter-laden pav buns on sides."},
    {"name": "Bengali Chitol Macher Muitha", "meal": "Lunch", "time": "45 Mins", "cal": "390 kcal", "img": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800", "ing": "Chitol fish paste, Boiled potato, Ginger-garlic, Garam masala, Mustard oil.", "met": "Shape spiced fish dumplings and poach in hot water. Fry golden and simmer in rich onion-ginger curry gravy."},
    {"name": "Fluffy Idli with Coconut Chutney", "meal": "Breakfast", "time": "15 Mins", "cal": "150 kcal", "img": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800", "ing": "Idli batter, Grated coconut, Roasted chana dal, Green chillies, Mustard tempering.", "met": "Steam batter in greased idli molds for 10 minutes. Blend coconut chutney and temper with curry leaves."},
    {"name": "Spicy Chicken Momos with Red Chutney", "meal": "Snacks", "time": "30 Mins", "cal": "260 kcal", "img": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800", "ing": "Minced chicken, Spring onions, Flour dough, Dry red chillies, Tomatoes.", "met": "Stuff rolled thin wrappers with seasoned chicken mince. Steam for 12 minutes. Serve with fiery red chilli dip."}
]

CHEF_STYLES = [
    "Dhaba Special", "Mughlai Style", "Homestyle Traditional", "Quick 15-Min", "Royal Nawabi", 
    "Healthy Detox", "Village Style", "Crispy Golden", "Restaurant Secret", "Grandma's Heritage"
]

def generate_daily_50_recipes():
    """প্রতিদিনের জন্য আলাদা ৫০টি নতুন রেসিপি তৈরির অ্যালগরিদম"""
    today_str = datetime.date.today().strftime("%Y%m%d")
    seed_val = int(today_str)
    rnd = random.Random(seed_val)
    
    recipes_list = []
    meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]
    
    for i in range(1, 51):
        base = rnd.choice(RECIPE_BASE_POOL)
        style = rnd.choice(CHEF_STYLES)
        meal_type = meals[(i - 1) % len(meals)]
        
        recipes_list.append({
            "id": i,
            "title": f"{style} {base['name']}",
            "meal": meal_type,
            "time": base["time"],
            "cal": base["cal"],
            "image": base["img"],
            "ingredients": base["ing"],
            "method": f"Chef's Daily Special: {base['met']} Garnish with fresh herbs and butter before serving."
        })
    return recipes_list

@app.route("/")
def home():
    news = sync_trending_news()
    lead = news[0] if news else None
    remaining = news[1:] if len(news) > 1 else []
    return render_template("index.html", lead=lead, news_list=remaining)

@app.route("/sync-news")
def force_sync():
    global LAST_FETCH_TIME
    LAST_FETCH_TIME = 0  # ক্যাশ মেয়াদ তৎক্ষণাৎ শূন্য করে দেওয়া
    sync_trending_news(force=True)
    return redirect(url_for("home"))

@app.route("/news/<int:news_id>")
def single_news(news_id):
    article = NEWS_DICT.get(news_id)
    if not article:
        load_from_disk()
        article = NEWS_DICT.get(news_id)
        if not article:
            abort(404)
    related = [n for n in CACHED_NEWS if n["id"] != news_id][:4]
    return render_template("single.html", article=article, related=related)

@app.route("/category/<cat_name>")
def category_view(cat_name):
    norm_cat = cat_name.lower()
    filtered = [n for n in CACHED_NEWS if n.get("category", "").lower() == norm_cat]
    if not filtered:
        filtered = CACHED_NEWS[:9]
    return render_template("category.html", category_name=cat_name.title(), news_list=filtered)

@app.route("/horoscope")
def horoscope_view():
    return render_template("horoscope.html")

# --- ৫০টি নিত্যনতুন রেসিপি রাউট (এক ক্লিকেই ওপেন হবে) ---
@app.route("/recipes")
def recipes_view():
    all_50 = generate_daily_50_recipes()
    meal_filter = request.args.get("meal")
    if meal_filter:
        filtered = [r for r in all_50 if r.get("meal", "").lower() == meal_filter.lower()]
        return render_template("recipes.html", recipes=filtered, today_date=datetime.date.today().strftime("%d %B, %Y"))
    return render_template("recipes.html", recipes=all_50, today_date=datetime.date.today().strftime("%d %B, %Y"))

@app.route("/recipes/<int:recipe_id>")
def single_recipe_view(recipe_id):
    all_50 = generate_daily_50_recipes()
    recipe = next((r for r in all_50 if r["id"] == recipe_id), None)
    if not recipe:
        abort(404)
    more = [r for r in all_50 if r["id"] != recipe_id][:3]
    return render_template("recipe_single.html", recipe=recipe, more_recipes=more)

@app.route("/privacy-policy")
def privacy_policy(): return render_template("privacy-policy.html")

@app.route("/terms")
def terms(): return render_template("terms.html")

@app.route("/disclaimer")
def disclaimer(): return render_template("disclaimer.html")

@app.route("/about")
def about(): return render_template("about.html")

@app.route("/contact")
def contact(): return render_template("contact.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
from flask import Response

@app.route("/sitemap.xml")
def sitemap():
    base_url = "https://news-portal-6alq.onrender.com"
    pages = [
        "", "/category/national", "/category/international", "/category/business",
        "/category/sports", "/category/entertainment", "/category/technology",
        "/category/science", "/horoscope", "/recipes", "/about", "/contact",
        "/privacy-policy", "/terms", "/disclaimer"
    ]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        xml.append(f"<url><loc>{base_url}{p}</loc><changefreq>hourly</changefreq><priority>0.8</priority></url>")
    
    for item in CACHED_NEWS[:60]:
        xml.append(f"<url><loc>{base_url}/news/{item['id']}</loc><changefreq>daily</changefreq><priority>1.0</priority></url>")
        
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")

@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")
# সমস্ত ব্রাউজার ক্যাশ বন্ধ রাখা যাতে হার্ড রিফ্রেশ ছাড়াই তৎক্ষণাৎ নতুন পেজ লোড হয়
@app.after_request
def set_response_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
from flask import jsonify

SHOWN_LEAD_IDS = set()

@app.route("/api/latest-lead")
def api_latest_lead():
    global SHOWN_LEAD_IDS, CACHED_NEWS
    # নতুন তাজা খবর ব্যাকগ্রাউন্ড সিঙ্ক করা
    sync_trending_news()
    
    # যে খবরগুলো এখনও দেখানো হয়নি সেগুলো খোঁজা
    unseen_news = [item for item in CACHED_NEWS if item["id"] not in SHOWN_LEAD_IDS]
    
    if not unseen_news:
        # সমস্ত খবর একবার দেখানো শেষ হলে পুল ক্লিয়ার করে নতুন সাইকেল শুরু
        SHOWN_LEAD_IDS.clear()
        unseen_news = CACHED_NEWS
        
    if unseen_news:
        selected = unseen_news[0]
        SHOWN_LEAD_IDS.add(selected["id"])
        return jsonify({
            "status": "success",
            "news": selected
        })
        
    return jsonify({"status": "empty"})