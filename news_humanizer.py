# -*- coding: utf-8 -*-
import re
import hashlib
from datetime import datetime

DATELINE_MAPPING = [
    ("delhi", "NEW DELHI"),
    ("india", "NEW DELHI"),
    ("mumbai", "MUMBAI"),
    ("bengaluru", "BENGALURU"),
    ("kolkata", "KOLKATA"),
    ("washington", "WASHINGTON"),
    ("us", "WASHINGTON"),
    ("america", "WASHINGTON"),
    ("russia", "MOSCOW"),
    ("ukraine", "KYIV"),
    ("london", "LONDON"),
    ("uk", "LONDON"),
    ("beijing", "BEIJING"),
    ("china", "BEIJING"),
    ("israel", "JERUSALEM"),
    ("iran", "TEHRAN"),
    ("tech", "SAN FRANCISCO"),
    ("cricket", "DUBAI")
]

def detect_dateline(text):
    text_low = text.lower()
    for key, city in DATELINE_MAPPING:
        if key in text_low:
            return city
    return "GLOBAL NEWS DESK"

def create_top_rank_headline(raw_title):
    # গুগল সার্চে সর্বোচ্চ ক্লিক রেট (CTR) পাওয়ার মতো হেডলাইন ফরম্যাটিং
    title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    title = re.sub(r'["\']', '', title)
    
    if not title:
        return "Breaking Report: Key Global Developments Unfold"
        
    power_prefixes = [
        "Breaking Dispatch:",
        "Special Investigation:",
        "Strategic Developments:",
        "High-Level Briefing:"
    ]
    hash_val = int(hashlib.md5(title.encode()).hexdigest(), 16)
    prefix = power_prefixes[hash_val % len(power_prefixes)]
    
    if len(title.split()) > 8:
        return title
    return f"{prefix} {title}"

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    raw_content = article.get("content", "") or ""
    img_url = article.get("urlToImage", "") or "https://24earlynews.com/static/favicon.svg"

    seo_title = create_top_rank_headline(raw_title)
    dateline = detect_dateline(seo_title + " " + raw_desc)
    current_date = datetime.now().strftime("%B %d, %Y")
    iso_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lead_text = raw_desc.strip() if raw_desc else f"Major developments unfolded regarding {seo_title}, triggering high-level administrative reviews and widespread attention across international monitoring circles."

    # ১. গুগল সার্চে ১ নম্বরে আসার জন্য ইনভার্টেড পিরামিড লিড
    lede_block = f"<p class='lead' style='font-size:17px;line-height:1.7;color:#1a1a1a;'><strong>{dateline}, {current_date} (24 Early News Special Bureau) — </strong> {lead_text}</p>"

    # ২. Google Featured Snippet (Answer Box) হাইলাইটস কার্ড
    snippet_box = (
        f"<div class='google-featured-take' style='background:#f9fbfd;border-left:4px solid #d32f2f;padding:15px 20px;margin:20px 0;border-radius:0 6px 6px 0;box-shadow:0 1px 4px rgba(0,0,0,0.06);'>"
        f"<h4 style='font-size:14px;letter-spacing:1px;color:#d32f2f;text-transform:uppercase;margin-bottom:10px;font-weight:800;'>Key Highlights & Strategic Takeaways</h4>"
        f"<ul style='margin:0;padding-left:18px;font-size:14px;color:#2c3e50;line-height:1.7;'>"
        f"<li><strong>Ground Assessment:</strong> Operational desks have initiated field assessments to maintain administrative control.</li>"
        f"<li><strong>Policy Impact:</strong> Market analysts and diplomatic observers note far-reaching implications across related sectors.</li>"
        f"<li><strong>Institutional Stance:</strong> Official channels emphasize adherence to formalized protocols as formal directives are released.</li>"
        f"</ul></div>"
    )

    # ৩. বিশ্লেষণধর্মী ব্যাকগ্রাউন্ড ও তথ্যবহুল বডি (EEAT স্ট্যান্ডার্ড)
    context_body = (
        "<p style='font-size:15px;line-height:1.8;color:#333;'>A thorough assessment of emerging dispatches indicates that the situation is developing in alignment with broader structural shifts. "
        "Independent policy specialists closely tracking the timeline emphasized that executive bodies are focusing on protocol enforcement to prevent potential operational friction. "
        "Historical precedents in comparable situations demonstrate that synchronized coordination between supervisory agencies and regional leadership remains critical for stabilizing forward trajectories.</p>"
    )

    # ৪. অথরিটেটিভ সমাপনী ও সাইন-অফ
    signoff_block = (
        "<p style='font-size:15px;line-height:1.8;color:#333;'>Spokespersons familiar with high-level briefings confirmed that formal communiqués will be disseminated through statutory channels. "
        "The 24 Early News Special Bureau maintains 24x7 active monitoring across all operational corridors and will furnish verified, corroborated dispatches as developments materialize.</p>"
    )

    # পূর্ণাঙ্গ আর্টিকেল
    full_story = f"{lede_block}\n{snippet_box}\n{context_body}\n{signoff_block}"

    return {
        "title": seo_title,
        "description": f"{dateline}: {lead_text}",
        "content": full_story,
        "url": article.get("url", "#"),
        "urlToImage": img_url,
        "publishedAt": article.get("publishedAt", "Live Update"),
        "source": {"name": "24 Early News Special Bureau"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]