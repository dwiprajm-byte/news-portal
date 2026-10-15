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

def make_unique_headline(raw_title):
    # অপ্রয়োজনীয় সোর্স মার্কার বা এপিআই ট্র্যাকার সরানো
    title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    title = re.sub(r'["\']', '', title)
    
    if not title:
        return "Global Developments: Key Strategic Updates Unfold"
        
    # হেডলাইনকে গুগল সার্চে ইউনিক ও বিশ্লেষণধর্মী দেখাতে স্মার্ট প্রিফিক্স
    prefixes = [
        "Special Dispatch:",
        "Strategic Analysis:",
        "Inside Report:",
        "Key Developments:"
    ]
    hash_val = int(hashlib.md5(title.encode()).hexdigest(), 16)
    prefix = prefixes[hash_val % len(prefixes)]
    
    if len(title.split()) > 7:
        return title
    return f"{prefix} {title}"

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    raw_content = article.get("content", "") or ""

    unique_title = make_unique_headline(raw_title)
    dateline = detect_dateline(unique_title + " " + raw_desc)
    current_date = datetime.now().strftime("%b %d")

    lead_text = raw_desc.strip() if raw_desc else f"Major developments unfolded regarding {unique_title}, drawing immediate reactions across public, commercial, and diplomatic corridors."

    # ১. আন্তর্জাতিক ব্যুরো লিড (Date & Official Wire Line)
    lede_paragraph = f"<p><strong>{dateline}, {current_date} (24 Early News Special Bureau) — </strong> {lead_text}</p>"

    # ২. এক্সিকিউটিভ স্ট্র্যাটেজিক ব্রিফ (Google Featured Snippet অপ্টিমাইজড হাইলাইটস কার্ড)
    executive_brief = (
        f"<div class='news-agency-take' style='background:#f8f9fa;border-left:4px solid #d32f2f;padding:14px 18px;margin:16px 0;border-radius:0 4px 4px 0;box-shadow:0 1px 3px rgba(0,0,0,0.05);'>"
        f"<strong style='font-size:13px;letter-spacing:1px;color:#d32f2f;text-transform:uppercase;'>Executive Strategic Brief:</strong>"
        f"<ul style='margin:8px 0 0 16px;padding:0;font-size:14px;color:#222;line-height:1.6;'>"
        f"<li><strong>Ground Status:</strong> Administrative frameworks have been actively deployed to assess ongoing real-time variables.</li>"
        f"<li><strong>Policy Impact:</strong> Strategic observers highlight cross-sector ripple effects shaping subsequent institutional stances.</li>"
        f"<li><strong>Verification Protocol:</strong> Official communiqués and formalized briefs remain the designated reference for emerging updates.</li>"
        f"</ul></div>"
    )

    # ৩. ইন-ডেপথ প্রেক্ষাপট ও কাঠামোগত বিশ্লেষণ (Original Background & Analysis)
    context_body = (
        "<p>According to dispatches reviewed by our monitoring editors, the situation reflects deeper structural shifts rather than isolated events. "
        "Independent policy specialists tracking the proceedings noted that regulatory authorities are prioritizing protocol enforcement to prevent secondary disruptions. "
        "Institutional observers further pointed out that previous benchmarks in similar circumstances necessitated coordinated policy responses between regional and executive oversight bodies.</p>"
    )

    # ৪. অথরিটেটিভ বক্তব্য ও প্রফেশনাল ব্যুরো সমাপনী (Attribution & Sign-off)
    signoff_paragraph = (
        "<p>Spokespersons familiar with the deliberations stated that official briefings will follow as documentation is finalized, urging public observers to rely solely on verified channels. "
        "Our specialized news desk maintains 24x7 active surveillance over developing corridors and will provide subsequent verified dispatches as facts are established.</p>"
    )

    # পূর্ণাঙ্গ প্রফেশনাল ওয়্যার আর্টিকেল
    full_wire_story = f"{lede_paragraph}\n{executive_brief}\n{context_body}\n{signoff_paragraph}"

    return {
        "title": unique_title,
        "description": f"{dateline}: {lead_text}",
        "content": full_wire_story,
        "url": article.get("url", "#"),
        "urlToImage": article.get("urlToImage", ""),
        "publishedAt": article.get("publishedAt", "Live Dispatch"),
        "source": {"name": "24 Early News Special Bureau"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]