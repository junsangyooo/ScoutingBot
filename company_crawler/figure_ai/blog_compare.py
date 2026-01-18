import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

FIGURE_BASE_URL = "https://www.figure.ai"
NEWS_URL = f"{FIGURE_BASE_URL}/news"


def _parse_iso_datetime_to_date(raw: str) -> str:
    """
    Example datetime attr:
    '2025-10-09T00:00:00.000Z'
    """
    if not raw:
        return ""
    try:
        # Handle trailing 'Z' (UTC)
        raw = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _extract_article(a_tag) -> Optional[Dict]:
    """
    Extracts a single article item from <a class="article-list-item" href="...">...</a>
    """
    href = a_tag.get("href")
    if not href:
        return None

    title_el = a_tag.select_one("h1.article-list-item__heading")
    time_el = a_tag.select_one("time.article-list-item__publication-date")

    title = title_el.get_text(strip=True) if title_el else ""
    date = ""
    if time_el:
        # Prefer machine-readable datetime attribute
        date = _parse_iso_datetime_to_date(time_el.get("datetime", "").strip())
        if not date:
            # Fallback: parse displayed text (e.g., "October 09, 2025")
            try:
                date = datetime.strptime(time_el.get_text(strip=True), "%B %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                date = ""

    return {
        "id": href,
        "title": title,
        "date": date,
        "type": "blog",   # per your schema
        "excerpt": "",
        "url": f"{FIGURE_BASE_URL}{href}",
    }


def figure_news_crawler() -> List[Dict]:
    resp = requests.get(NEWS_URL, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items: List[Dict] = []

    # =====================
    # Featured posts
    # =====================
    featured_links = soup.select(
        "div.article-list__featured-articles ol.article-list__featured-articles-list "
        "a.article-list-item[href]"
    )
    for a in featured_links:
        article = _extract_article(a)
        if article:
            # Optional: mark as featured without changing schema
            # article["featured"] = True
            items.append(article)

    # =====================
    # Main list posts
    # =====================
    main_links = soup.select(
        "div.article-list__main ul.article-list__list a.article-list-item[href]"
    )
    for a in main_links:
        article = _extract_article(a)
        if article:
            items.append(article)

    # De-duplicate by id while preserving order (featured can overlap with main)
    seen = set()
    deduped = []
    for it in items:
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        deduped.append(it)

    return deduped
