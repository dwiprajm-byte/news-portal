import os, re, html, hashlib, sqlite3, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from threading import Lock
from flask import Flask, render_template, request, abort

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "news.sqlite3"))
REFRESH_MINUTES = max(1, int(os.environ.get("NEWS_REFRESH_MINUTES", "10")))
SECRET_KEY = os.environ.get("SECRET_KEY", "24earlynews-local-development-key-change-in-production")
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
_refresh_lock = Lock()

RSS_FEEDS = {
    "India": "https://news.google.com/rss/search?q=India+breaking+news&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=World+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Business": "https://news.google.com/rss/search?q=India+business+markets&hl=en-IN&gl=IN&ceid=IN:en",
    "Tech": "https://news.google.com/rss/search?q=technology+AI&hl=en-IN&gl=IN&ceid=IN:en",
    "Sports": "https://news.google.com/rss/search?q=sports+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Cricket": "https://news.google.com/rss/search?q=cricket&hl=en-IN&gl=IN&ceid=IN:en",
    "Entertainment": "https://news.google.com/rss/search?q=Bollywood+entertainment&hl=en-IN&gl=IN&ceid=IN:en",
    "Auto": "https://news.google.com/rss/search?q=automobile+cars&hl=en-IN&gl=IN&ceid=IN:en",
    "Cities": "https://news.google.com/rss/search?q=Kolkata+West+Bengal+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Trending": "https://news.google.com/rss/search?q=India+trending+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Education": "https://news.google.com/rss/search?q=India+education+exam+results&hl=en-IN&gl=IN&ceid=IN:en",
}

def db():
    conn = sqlite3.connect(DB_FILE, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=20000")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_FILE) or BASE_DIR, exist_ok=True)
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS app_meta (key TEXT PRIMARY KEY, value TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL, category TEXT NOT NULL, published TEXT,
            image TEXT, summary TEXT, content TEXT, source_name TEXT,
            source_url TEXT NOT NULL, created_at TEXT NOT NULL,
            language TEXT DEFAULT 'en')""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_news_category ON news(category)")

def clean_text(value):
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()

def make_slug(title, url):
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:65] or "news"
    suffix = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"{base}-{suffix}"

def parse_date(value):
    if value:
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat(timespec="seconds")
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def refresh_news(force=False):
    # DB-level timestamp gate prevents each web worker from fetching on every page view.
    with _refresh_lock:
        now = datetime.now(timezone.utc)
        with db() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT value FROM app_meta WHERE key='last_refresh_started'").fetchone()
            if not force and row:
                try:
                    last = datetime.fromisoformat(row["value"])
                    if last.tzinfo is None:
                        last = last.replace(tzinfo=timezone.utc)
                    if now - last < timedelta(minutes=REFRESH_MINUTES):
                        con.commit()
                        return 0
                except Exception:
                    pass
            con.execute("INSERT INTO app_meta(key,value) VALUES('last_refresh_started',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (now.isoformat(),))
            con.commit()

        added = 0
        headers = {"User-Agent": "Mozilla/5.0 (compatible; 24EarlyNews/1.0; +https://24earlynews.com)"}
        for category, feed_url in RSS_FEEDS.items():
            try:
                req = urllib.request.Request(feed_url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    root = ET.fromstring(response.read())
                for item in root.findall("./channel/item"):
                    title = clean_text(item.findtext("title"))
                    link = clean_text(item.findtext("link"))
                    if not title or not link or not link.startswith(("http://", "https://")):
                        continue
                    source_node = item.find("source")
                    source_name = clean_text(source_node.text if source_node is not None else "") or "Google News feed"
                    description = clean_text(item.findtext("description"))
                    published = parse_date(item.findtext("pubDate"))
                    slug = make_slug(title, link)
                    with db() as con:
                        exists = con.execute("SELECT 1 FROM news WHERE source_url=? OR slug=? LIMIT 1", (link, slug)).fetchone()
                        if exists:
                            continue
                        con.execute("""INSERT INTO news
                            (slug,title,category,published,image,summary,content,source_name,source_url,created_at,language)
                            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                            (slug, title, category, published, "", description[:500], description,
                             source_name, link, now.isoformat(), "en"))
                        added += 1
            except Exception as exc:
                app.logger.warning("RSS refresh failed for %s: %s", category, exc)
        with db() as con:
            con.execute("INSERT INTO app_meta(key,value) VALUES('last_refresh_completed',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (datetime.now(timezone.utc).isoformat(),))
        app.logger.info("RSS refresh complete; added %s articles", added)
        return added

def row_to_dict(row):
    return dict(row) if row else None

@app.route("/")
def index():
    refresh_news()
    category = (request.args.get("cat") or "").strip()
    search = (request.args.get("q") or "").strip()
    page = max(1, request.args.get("page", 1, type=int) or 1)
    per_page = 18
    clauses, params = [], []
    if category and category.lower() not in ("latest", "all"):
        clauses.append("LOWER(category)=LOWER(?)"); params.append(category)
    if search:
        clauses.append("(title LIKE ? OR summary LIKE ? OR source_name LIKE ?)")
        term = f"%{search}%"; params.extend([term, term, term])
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with db() as con:
        total = con.execute("SELECT COUNT(*) FROM news" + where, params).fetchone()[0]
        items = con.execute("SELECT * FROM news" + where + " ORDER BY COALESCE(published,created_at) DESC, id DESC LIMIT ? OFFSET ?", params + [per_page, (page-1)*per_page]).fetchall()
        categories = con.execute("SELECT category, COUNT(*) AS total FROM news GROUP BY category ORDER BY category").fetchall()
    return render_template("index.html", news=[row_to_dict(x) for x in items], categories=categories,
                           category=category, search=search, page=page, total_pages=max(1,(total+per_page-1)//per_page), total=total)

@app.route("/news/<slug>")
def detail(slug):
    with db() as con:
        article = con.execute("SELECT * FROM news WHERE slug=?", (slug,)).fetchone()
    if not article:
        abort(404)
    return render_template("detail.html", article=row_to_dict(article))

@app.route("/search")
def search():
    return index()

@app.route("/about")
def about(): return render_template("about.html")
@app.route("/privacy")
def privacy(): return render_template("privacy.html")
@app.route("/terms")
def terms(): return render_template("terms.html")
@app.route("/contact")
def contact(): return render_template("contact.html")

@app.route("/health")
def health():
    with db() as con:
        count = con.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    return {"status":"ok", "news_count":count}

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
