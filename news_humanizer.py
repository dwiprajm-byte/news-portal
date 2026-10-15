# -*- coding: utf-8 -*-
import re

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
    ("moscow", "MOSCOW"),
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
    return "NEW DELHI"

def format_as_bullet_highlights(lead_text, title):
    # সংবাদের ৩টি মূল হাইলাইটস তৈরি
    p1 = f"Key developments confirmed regarding {title}."
    p2 = lead_text if lead_text else "Administrative authorities and observer desks are closely reviewing ground assessments."
    p3 = "Official directives have been notified as emergency and regulatory desks maintain heightened vigilance."
    
    return (
        f"<div class='news-highlights-box' style='background:#f9f9f9;border-left:4px solid #d32f2f;padding:12px 16px;margin:15px 0;border-radius:0 6px 6px 0;'>"
        f"<strong style='font-size:14px;color:#111;text-transform:uppercase;'>Key Highlights:</strong>"
        f"<ul style='margin:8px 0 0 18px;padding:0;font-size:14px;color:#333;line-height:1.6;'>"
        f"<li>{p1}</li>"
        f"<li>{p2}</li>"
        f"<li>{p3}</li>"
        f"</ul></div>"
    )

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    raw_content = article.get("content", "") or ""
    
    # অপ্রয়োজনীয় সোর্স মার্কার বা এপিআই ক্লিনিং
    clean_title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    if not clean_title:
        clean_title = "Global News Report: Key Highlights And Emerging Developments"
    clean_title = re.sub(r'["\']', '', clean_title)

    # ১. ডেটলাইন চিহ্নিত করা
    dateline = detect_dateline(clean_title + " " + raw_desc)

    # ২. লিড প্যারাগ্রাফ (Lede)
    lead_summary = raw_desc.strip() if raw_desc else f"High-level developments were reported today concerning {clean_title}, drawing immediate reactions across regional and international diplomatic circles."
    lead_paragraph = f"<p><strong>{dateline}: </strong> {lead_summary}</p>"

    # ৩. হাইলাইটস বক্স
    highlights_block = format_as_bullet_highlights(lead_summary, clean_title)

    # ৪. ইনভার্টেড পিরামিড বডি প্যারাগ্রাফ (Body & Context)
    body_paragraph = (
        "<p>According to information shared by monitoring officials and desk correspondents, the matter is under active review by operational authorities. "
        "Independent policy analysts emphasize that these developments carry strategic weight, particularly as regulatory bodies seek to address immediate ripple effects on the ground. "
        "Ground security and monitoring protocols have been alerted to respond to emerging situations promptly.</p>"
    )

    # ৫. অফিশিয়াল কোট/রেসপন্স ও সমাপনী (Sign-off)
    closing_paragraph = (
        "<p>Administrative spokespersons have reiterated that verified updates will be issued through official gazettes and accredited press briefs. "
        "Our specialized news desk continues to follow the timeline of events closely and will bring verified on-ground dispatches as further facts are established.</p>"
    )

    # পূর্ণাঙ্গ পেশাদার জার্নালিস্টিক আর্টিকেল
    structured_content = f"{lead_paragraph}\n{highlights_block}\n{body_paragraph}\n{closing_paragraph}"

    return {
        "title": clean_title,
        "description": f"{dateline}: {lead_summary}",
        "content": structured_content,
        "url": article.get("url", "#"),
        "urlToImage": article.get("urlToImage", ""),
        "publishedAt": article.get("publishedAt", "Live Update"),
        "source": {"name": "24 Early News Special Bureau"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]