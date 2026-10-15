# -*- coding: utf-8 -*-
import re

DATELINE_CITIES = [
    ("india", "NEW DELHI"),
    ("delhi", "NEW DELHI"),
    ("mumbai", "MUMBAI"),
    ("bengaluru", "BENGALURU"),
    ("us", "WASHINGTON"),
    ("america", "WASHINGTON"),
    ("russia", "MOSCOW"),
    ("ukraine", "KYIV"),
    ("uk", "LONDON"),
    ("london", "LONDON"),
    ("china", "BEIJING"),
    ("israel", "JERUSALEM"),
    ("cricket", "DUBAI"),
    ("tech", "SAN FRANCISCO")
]

def get_appropriate_dateline(text):
    text_lower = text.lower()
    for keyword, city in DATELINE_CITIES:
        if keyword in text_lower:
            return city
    return "NEW DELHI / GLOBAL DESK"

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    raw_content = article.get("content", "") or ""
    
    # অপ্রয়োজনীয় ট্র্যাকিং ও স্ক্র্যাপ মার্কার ক্লিন করা
    clean_title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    if not clean_title:
        clean_title = "Global News Report: Key Highlights And Emerging Developments"

    clean_title = re.sub(r'["\']', '', clean_title)

    # সঠিক ব্যুরো ডেসপ্যাচ লোকেশন নির্ধারণ
    dateline = get_appropriate_dateline(clean_title + " " + raw_desc)

    # ১. স্ট্রং লিড প্যারাগ্রাফ (Lead Story Paragraph)
    lead_text = raw_desc.strip() if raw_desc else f"Significant developments unfolded today regarding {clean_title}, drawing immediate attention from key stakeholders and international observers."
    dispatch_lead = f"<b>{dateline}: </b> {lead_text}"

    # ২. অ্যানালাইটিকাল বডি ও প্রেক্ষাপট (Context & Ground Reality)
    dispatch_body = (
        "According to official sources closely tracking the matter, administrative and monitoring teams are reviewing the broader implications. "
        "Independent analysts point out that this move comes amid shifting regional and global dynamics, making it a critical talking point across policy and public circles. "
        "Ground reports indicate that protocols have been alerted to address ongoing updates swiftly."
    )

    # ৩. অফিসিয়াল সাইন-অফ ও সমাপনী (Official Response & Sign-off)
    dispatch_conclusion = (
        "Authorities have urged stakeholders to rely exclusively on verified communications as formal briefs are compiled. "
        "Our editorial desk continues to monitor the ground situation and will bring further verified updates as they emerge."
    )

    # ৩-স্তরের পূর্ণাঙ্গ সম্পাদকীয় সংবাদ
    full_article_content = f"{dispatch_lead}\n\n{dispatch_body}\n\n{dispatch_conclusion}"

    return {
        "title": clean_title,
        "description": f"{dateline}: {lead_text}",
        "content": full_article_content,
        "url": article.get("url", "#"),
        "urlToImage": article.get("urlToImage", ""),
        "publishedAt": article.get("publishedAt", "Live Update"),
        "source": {"name": "24 Early News Special Bureau"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]