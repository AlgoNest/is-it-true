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
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200 or len(r.text) < 500:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        blocks = soup.find_all(["article", "section", "div", "p"])
        extracted = []

        for b in blocks:
            text = b.get_text(" ", strip=True)
            if len(text) > 120 and any(h in text.lower() for h in COMPLAINT_HINTS):
                extracted.append(text)

        if not extracted:
            return None

        return " ".join(extracted[:3])

    except Exception:
        return None

# -------------------------------------------------
# Reddit search
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
# DuckDuckGo search (Discovery only)
# -------------------------------------------------
def search_duckduckgo(query, max_results=10):
    results = []
    params = {"q": f"{query} complaint problem issue", "kl": "us-en"}
    url = "https://html.duckduckgo.com/html/?" + urlencode(params)

    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
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
# Trustpilot
# -------------------------------------------------
def search_trustpilot(query, max_results=10):
    results = []
    search_url = f"https://www.trustpilot.com/search?query={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        reviews = soup.select(".review-content")

        for rev in reviews[:max_results]:
            text = rev.get_text(" ", strip=True)
            if len(text) > 100 and any(k in text.lower() for k in COMPLAINT_HINTS):
                results.append({
                    "title": f"{query} review",
                    "excerpt": text[:200],
                    "url": search_url,
                    "source": "Trustpilot"
                })

    except Exception:
        return results

    return results

# -------------------------------------------------
# SiteJabber
# -------------------------------------------------
def search_sitejabber(query, max_results=10):
    results = []
    search_url = f"https://www.sitejabber.com/reviews/search?query={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        reviews = soup.select(".review")

        for rev in reviews[:max_results]:
            text = rev.get_text(" ", strip=True)
            if len(text) > 100 and any(k in text.lower() for k in COMPLAINT_HINTS):
                results.append({
                    "title": f"{query} review",
                    "excerpt": text[:200],
                    "url": search_url,
                    "source": "SiteJabber"
                })

    except Exception:
        return results

    return results

# -------------------------------------------------
# ComplaintsBoard
# -------------------------------------------------
def search_complaintsboard(query, max_results=10):
    results = []
    search_url = f"https://www.complaintsboard.com/search?query={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        complaints = soup.select(".postcontent")

        for c in complaints[:max_results]:
            text = c.get_text(" ", strip=True)
            if len(text) > 100 and any(k in text.lower() for k in COMPLAINT_HINTS):
                results.append({
                    "title": f"{query} complaint",
                    "excerpt": text[:200],
                    "url": search_url,
                    "source": "ComplaintsBoard"
                })

    except Exception:
        return results

    return results

# -------------------------------------------------
# RipoffReport
# -------------------------------------------------
def search_ripoffreport(query, max_results=10):
    results = []
    search_url = f"https://www.ripoffreport.com/search?query={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        complaints = soup.select(".report-summary")

        for c in complaints[:max_results]:
            text = c.get_text(" ", strip=True)
            if len(text) > 100 and any(k in text.lower() for k in COMPLAINT_HINTS):
                results.append({
                    "title": f"{query} report",
                    "excerpt": text[:200],
                    "url": search_url,
                    "source": "RipoffReport"
                })

    except Exception:
        return results

    return results

# -------------------------------------------------
# ConsumerAffairs
# -------------------------------------------------
def search_consumeraffairs(query, max_results=10):
    results = []
    search_url = f"https://www.consumeraffairs.com/search/?query={query}"

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return results

        soup = BeautifulSoup(r.text, "html.parser")
        reviews = soup.select(".rvw-bd")

        for rev in reviews[:max_results]:
            text = rev.get_text(" ", strip=True)
            if len(text) > 100 and any(k in text.lower() for k in COMPLAINT_HINTS):
                results.append({
                    "title": f"{query} review",
                    "excerpt": text[:200],
                    "url": search_url,
                    "source": "ConsumerAffairs"
                })

    except Exception:
        return results

    return results

# -------------------------------------------------
# MAIN FUNCTION (DO NOT RENAME)
# -------------------------------------------------
def search_complaints(query, max_total=40):
    final_results = []
    seen_urls = set()

    # Priority order: Reddit first, then other sources
    sources = [
        search_reddit,
        search_trustpilot,
        search_sitejabber,
        search_complaintsboard,
        search_ripoffreport,
        search_consumeraffairs,
        search_duckduckgo
    ]

    for src in sources:
        results = src(query, max_results=max_total)
        for r in results:
            if r["url"] not in seen_urls:
                final_results.append(r)
                seen_urls.add(r["url"])
            if len(final_results) >= max_total:
                break
        if len(final_results) >= max_total:
            break

    return final_results[:max_total]
