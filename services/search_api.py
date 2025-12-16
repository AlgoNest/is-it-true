import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

# --- Reddit search ---
def search_reddit(query, max_results=15):
    results = []
    search_terms = [f"{query} problem", f"{query} issue", f"{query} complaint"]

    for term in search_terms:
        url = "https://www.reddit.com/search.json"
        params = {"q": term, "limit": 8, "sort": "relevance", "sr_detail": 1}

        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=5)
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception:
            continue

        for post in data.get("data", {}).get("children", []):
            p = post["data"]
            text = p.get("selftext", "")
            if len(text) > 50:
                results.append({
                    "title": p["title"],
                    "excerpt": text[:180],
                    "url": f"https://reddit.com{p['permalink']}",
                    "source": "Reddit"
                })

    return results[:max_results]

# --- Hacker News search ---
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
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        if title:
            results.append({
                "title": title,
                "excerpt": title,  # HN stories usually don't have body text
                "url": url,
                "source": "Hacker News"
            })
    return results

# --- Main function: combine all sources ---
def search_complaints(query, max_total=25):
    results = []

    # Reddit
    reddit_results = search_reddit(query, max_results=15)
    results.extend(reddit_results)

    # Hacker News
    hn_results = search_hn(query, max_results=10)
    # Avoid duplicate URLs
    urls = {r["url"] for r in results}
    for r in hn_results:
        if r["url"] not in urls:
            results.append(r)

    # Optionally: more sources here

    return results[:max_total]
