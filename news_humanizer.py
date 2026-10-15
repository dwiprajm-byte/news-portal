# -*- coding: utf-8 -*-
import re
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

def clean_headline(raw_title):
    title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    title = re.sub(r'["\']', '', title)
    return title if title else "Global Developments: Key Strategic Updates Unfold"

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    raw_content = article.get("content", "") or ""

    clean_title = clean_headline(raw_title)
    dateline = detect_dateline(clean_title + " " + raw_desc)
    current_date = datetime.now().strftime("%B %d, %Y")

    lead_text = raw_desc.strip() if raw_desc else f"Major developments unfolded regarding {clean_title}, drawing immediate reactions across public, commercial, and diplomatic corridors."

    # ১. গুগল সার্চে ১ নম্বরে আনার জন্য সুনির্দিষ্ট প্রাতিষ্ঠানিক লিড
    lede_paragraph = f"<p class='lead' style='font-size:16px;line-height:1.75;color:#111;'><strong>{dateline}, {current_date} (24 Early News Special Bureau) — </strong> {lead_text}</p>"

    # ২. Google Featured Snippet (Answer Box) হাইলাইটস কার্ড
    executive_brief = (
        f"<div class='news-agency-take' style='background:#f8f9fa;border-left:4px solid #d32f2f;padding:14px 18px;margin:18px 0;border-radius:0 4px 4px 0;box-shadow:0 1px 3px rgba(0,0,0,0.05);'>"
        f"<h4 style='font-size:13px;letter-spacing:1px;color:#d32f2f;text-transform:uppercase;margin-bottom:8px;font-weight:800;'>Strategic Overview & Key Highlights</h4>"
        f"<ul style='margin:0;padding-left:18px;font-size:14px;color:#222;line-height:1.65;'>"
        f"<li><strong>Ground Reality:</strong> Operational teams have initiated evaluations to maintain oversight on evolving developments.</li>"
        f"<li><strong>Policy Impact:</strong> Cross-sector analysts identify immediate ripple effects shaping upcoming regulatory guidelines.</li>"
        f"<li><strong>Verification Standard:</strong> Formal government statements remain the definitive reference point for emerging facts.</li>"
        f"</ul></div>"
    )

    # ৩. ইন-ডেপথ প্রেক্ষাপট ও কাঠামোগত বিশ্লেষণ
    context_body = (
        "<p style='font-size:15px;line-height:1.8;color:#333;'>A detailed examination by monitoring editors indicates that the ongoing situation is tied to broader structural transitions. "
        "Independent policy specialists closely tracking the timeline emphasized that executive bodies are focusing on protocol enforcement to prevent potential operational friction. "
        "Historical precedents in comparable situations demonstrate that synchronized coordination between supervisory agencies and regional leadership remains critical for stabilizing forward trajectories.</p>"
    )

    # ৪. অথরিটেটিভ বক্তব্য ও প্রফেশনাল ব্যুরো সমাপনী
    signoff_paragraph = (
        "<p style='font-size:15px;line-height:1.8;color:#333;'>Spokespersons familiar with high-level briefings confirmed that formal communiqués will be disseminated through statutory channels. "
        "The 24 Early News Special Bureau maintains 24x7 active monitoring across all operational corridors and will furnish verified, corroborated dispatches as developments materialize.</p>"
    )

    full_story = f"{lede_paragraph}\n{executive_brief}\n{context_body}\n{signoff_paragraph}"

    return {
        "title": clean_title,
        "description": f"{dateline}: {lead_text}",
        "content": full_story,
        "url": article.get("url", "#"),
        "urlToImage": article.get("urlToImage", ""),
        "publishedAt": article.get("publishedAt", "Live Dispatch"),
        "source": {"name": "24 Early News Special Bureau"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]