import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

# Domains we don’t want to include
BAD_DOMAINS = [
    "google.com", "youtube.com", "facebook.com",
    "twitter.com", "linkedin.com", "instagram.com"
]

# -------------------------------
# Extract text from a URL (fallback)
# -------------------------------
def extract_report_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        if len(text) < 50:
            return None
        return text[:250]
    except Exception:
        return None

# -------------------------------
# Reddit search
# -------------------------------
def search_reddit(query, max_results=15):
    results = []
    search_terms = [f"{query} problem", f"{query} issue", f"{query} complaint", f"{query} scam"]

    for term in search_terms:
        try:
            r = requests.get(
                "https://www.reddit.com/search.json",
                params={"q": term, "limit": 10, "sort": "relevance"},
                headers=HEADERS,
                timeout=6
            )
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception:
            continue

        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            text = p.get("selftext", "")
            results.append({
                "title": p.get("title"),
                "excerpt": text[:200] if text else "See full post",
                "url": f"https://reddit.com{p.get('permalink')}",
                "source": "Reddit"
            })
        if len(results) >= max_results:
            break

    return results[:max_results]

# -------------------------------
# Hacker News search
# -------------------------------
def search_hn(query, max_results=10):
    results = []
    url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&hitsPerPage={max_results}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return results
        data = r.json()
    except Exception:
        return results

    for hit in data.get("hits", []):
        title = hit.get("title")
        url_hit = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        results.append({
            "title": title,
            "excerpt": title[:200] if title else "Hacker News post",
            "url": url_hit,
            "source": "Hacker News"
        })
    return results

# -------------------------------
# DuckDuckGo HTML search
# -------------------------------
def search_duckduckgo(query, max_results=10):
    results = []
    params = {"q": f"{query} complaint problem issue", "kl": "us-en"}
    url = "https://html.duckduckgo.com/html/?" + urlencode(params)
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select(".result__a")

        for link in links:
            href = link.get("href")
            title = link.get_text(strip=True)
            if not href or any(bad in href for bad in BAD_DOMAINS):
                continue

            text = extract_report_text(href)
            if not text:
                text = "Click link to view report"

            results.append({
                "title": title,
                "excerpt": text[:200],
                "url": href,
                "source": "Web"
            })
            if len(results) >= max_results:
                break
    except Exception:
        return results

    return results

# -------------------------------
# MAIN SEARCH FUNCTION
# -------------------------------
def search_complaints(query, max_total=30):
    final_results = []
    seen_urls = set()

    sources = [search_reddit, search_hn, search_duckduckgo]

    for src in sources:
        try:
            results = src(query, max_total)
        except Exception:
            results = []

        for r in results:
            if r["url"] not in seen_urls:
                final_results.append(r)
                seen_urls.add(r["url"])
            if len(final_results) >= max_total:
                break

        if len(final_results) >= max_total:
            break

    return final_results[:max_total]
