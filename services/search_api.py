import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

BAD_DOMAINS = [
    "duckduckgo.com",
    "google.com",
    "youtube.com",
    "facebook.com",
    "twitter.com",
    "linkedin.com",
    "instagram.com"
]

COMPLAINT_HINTS = [
    "problem", "issue", "complaint", "refund", "scam",
    "not working", "bad service", "poor", "delay", "fraud"
]

# -------------------------------------------------
# Extract REAL report text from a linked page
# -------------------------------------------------
def extract_report_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200 or len(r.text) < 500:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        blocks = soup.find_all(["article", "section", "div", "p"])

        extracted = []
        for b in blocks:
            text = b.get_text(" ", strip=True)
            if (
                len(text) > 120
                and any(h in text.lower() for h in COMPLAINT_HINTS)
            ):
                extracted.append(text)

        if not extracted:
            return None

        return " ".join(extracted[:3])

    except Exception:
        return None

# -------------------------------------------------
# Reddit search (PRIMARY SOURCE)
# -------------------------------------------------
def search_reddit(query, max_results=15):
    results = []
    terms = [
        f"{query} problem",
        f"{query} issue",
        f"{query} complaint",
        f"{query} scam"
    ]

    for term in terms:
        try:
            r = requests.get(
                "https://www.reddit.com/search.json",
                params={"q": term, "limit": 30, "sort": "relevance"},
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

            if len(text) < 80:
                continue

            results.append({
                "title": p.get("title"),
                "excerpt": text[:200],
                "url": f"https://reddit.com{p.get('permalink')}",
                "source": "Reddit"
            })

        if len(results) >= max_results:
            break

    return results[:max_results]

# -------------------------------------------------
# DuckDuckGo (DISCOVERY ONLY – content is scraped)
# -------------------------------------------------
def search_duckduckgo(query, max_results=20):
    results = []
    params = {
        "q": f"{query} complaint problem issue",
        "kl": "us-en"
    }

    url = "https://html.duckduckgo.com/html/?" + urlencode(params)

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select(".result__a")

        for link in links:
            href = link.get("href")
            title = link.get_text(strip=True)

            if not href or any(bad in href for bad in BAD_DOMAINS):
                continue

            report = extract_report_text(href)
            if not report:
                continue

            results.append({
                "title": title,
                "excerpt": report[:200],
                "url": href,
                "source": "Web"
            })

            if len(results) >= max_results:
                break

    except Exception:
        return results

    return results

# -------------------------------------------------
# MAIN ENTRY POINT (DO NOT RENAME)
# -------------------------------------------------
def search_complaints(query, max_total=25):
    final_results = []
    seen_urls = set()

    # 1️⃣ Reddit first (highest quality)
    reddit_results = search_reddit(query, max_results=15)
    for r in reddit_results:
        if r["url"] not in seen_urls:
            final_results.append(r)
            seen_urls.add(r["url"])

    # 2️⃣ DuckDuckGo fallback (only real reports)
    if len(final_results) < max_total:
        web_results = search_duckduckgo(
            query,
            max_results=max_total - len(final_results)
        )

        for r in web_results:
            if r["url"] not in seen_urls:
                final_results.append(r)
                seen_urls.add(r["url"])

    return final_results[:max_total]
