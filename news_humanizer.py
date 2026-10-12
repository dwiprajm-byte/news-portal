# -*- coding: utf-8 -*-
import re

def humanize_article(article):
    raw_title = article.get("title", "") or ""
    raw_desc = article.get("description", "") or ""
    
    clean_title = re.sub(r'\s*-\s*[A-Za-z0-9\s\.\-]+$', '', raw_title).strip()
    if not clean_title:
        clean_title = "Global News Report"
        
    lead = (
        f"WORLD DESK — In a developing report, {raw_desc.strip()} "
        if raw_desc else f"WORLD DESK — Officials and international observers are closely tracking developments surrounding {clean_title}."
    )
    
    body = (
        "Key stakeholders and regulatory analysts have noted that the situation represents a pivotal development with significant broader implications. "
        "Independent verification and ongoing assessments continue as regional agencies respond to emerging updates."
    )
    
    conclusion = (
        "Further official statements are anticipated in the coming hours as facts are reviewed and finalized. "
        "Our editorial desk continues to follow the situation closely."
    )
    
    full_humanized_content = f"{lead}\n\n{body}\n\n{conclusion}"
    
    return {
        "title": clean_title,
        "description": lead,
        "content": full_humanized_content,
        "url": article.get("url", "#"),
        "urlToImage": article.get("urlToImage", ""),
        "publishedAt": article.get("publishedAt", "Recent Update"),
        "source": {"name": "24 Early News International Desk"}
    }

def process_articles_list(articles):
    if not articles:
        return []
    return [humanize_article(art) for art in articles]