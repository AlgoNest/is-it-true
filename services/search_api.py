import requests
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

# ---------- Helpers ----------

def _clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _normalize_query(query):
    return re.sub(r"\s+", " ", query.strip())

def _is_complaint_text(text):
    text = text.lower()
    keywords = [
        "problem", "issue", "complaint", "scam", "fraud",
        "bad", "worst", "broken", "delay", "refund",
        "support", "service", "fail", "error", "hate"
    ]
    return any(k in text for k in keywords)

# ---------- Reddit ----------

def search_reddit(query, max_results=15):
    results = []
    seen_urls = set()
    query = _normalize_query(query)

    if not query:
        return results

    search_terms = [
        query,
        f"{query} problem",
        f"{query} issue",
        f"{query} complaint",
        f"{query} scam",
        f"{query} review"
    ]

    for term in search_terms:
        after = None
        pages = 0

        while pages < 2 and len(results) < max_results:
            params = {
                "q": term,
                "limit": 10,
                "sort": "relevance",
                "after": after
            }

            try:
                r = requests.get(
                    "https://www.reddit.com/search.json",
                    headers=HEADERS,
                    params=params,
                    timeout=6
                )
                if r.status_code != 200:
                    break
                data = r.json()
            except Exception:
                break

            posts = data.get("data", {}).get("children", [])
            after = data.get("data", {}).get("after")
            pages += 1

            for post in posts:
                p = post.get("data", {})
                url = f"https://reddit.com{p.get('permalink', '')}"
                if not url or url in seen_urls:
                    continue

                title = _clean_text(p.get("title", ""))
                body = _clean_text(p.get("selftext", ""))

                combined = f"{title} {body}"
                if len(combined) < 80 or not _is_complaint_text(combined):
                    continue

                seen_urls.add(url)
                results.append({
                    "title": title,
                    "excerpt": body[:200] if body else title[:200],
                    "url": url,
                    "source": "Reddit"
                })

                if len(results) >= max_results:
                    break

            if not after:
                break

    return results[:max_results]

# ---------- Hacker News ----------

def search_hn(query, max_results=10):
    results = []
    seen_urls = set()
    query = _normalize_query(query)

    if not query:
        return results

    url = (
        "https://hn.algolia.com/api/v1/search?"
        f"query={quote_plus(query)}&tags=story&hitsPerPage={max_results * 2}"
    )

    try:
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return results
        data = r.json()
    except Exception:
        return results

    for hit in data.get("hits", []):
        title = _clean_text(hit.get("title", ""))
        link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

        if not title or link in seen_urls:
            continue
        if not _is_complaint_text(title):
            continue

        seen_urls.add(link)
        results.append({
            "title": title,
            "excerpt": title[:200],
            "url": link,
            "source": "Hacker News"
        })

        if len(results) >= max_results:
            break

    return results

# ---------- DuckDuckGo Web Search (Complaints Articles) ----------

def search_web(query, max_results=10):
    results = []
    seen_urls = set()

    search_query = f"{query} complaint OR problem OR scam"
    url = f"https://duckduckgo.com/html/?q={quote_plus(search_query)}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code != 200:
            return results
    except Exception:
        return results

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select(".result__a")

    for link in links:
        href = link.get("href")
        title = _clean_text(link.get_text())

        if not href or href in seen_urls:
            continue
        if not _is_complaint_text(title):
            continue

        seen_urls.add(href)
        results.append({
            "title": title,
            "excerpt": title[:200],
            "url": href,
            "source": "Web"
        })

        if len(results) >= max_results:
            break

    return results

# ---------- Main Aggregator ----------

def search_complaints(query, max_total=25):
    results = []
    seen_urls = set()
    query = _normalize_query(query)

    if not query:
        return results

    for source_results in [
        search_reddit(query, 20),
        search_web(query, 15),
        search_hn(query, 10)
    ]:
        for r in source_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                results.append(r)
            if len(results) >= max_total:
                break

    if not results:
        results.append({
            "title": f"No major complaints found for '{query}'",
            "excerpt": "This could mean users are not reporting many public issues.",
            "url": "",
            "source": "System"
        })

    return results[:max_total]
