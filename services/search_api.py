import requests

HEADERS = {
    "User-Agent": "is-it-true-app"
}

def search_complaints(query):
    results = []
    search_terms = [
        f"{query} problem",
        f"{query} issue",
        f"{query} complaint"
    ]

    for term in search_terms:
        url = "https://www.reddit.com/search.json"
        params = {
            "q": term,
            "limit": 8,
            "sort": "relevance"
        }

        r = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=5
        )

        if r.status_code != 200:
            continue

        data = r.json()

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

    return results[:25]
