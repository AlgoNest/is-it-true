import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="complaint-search-app"
)

def search_complaints(query):
    results = []
    search_terms = [
        f"{query} problem",
        f"{query} issue",
        f"{query} complaint"
    ]

    for term in search_terms:
        for post in reddit.subreddit("all").search(term, limit=8):
            if post.selftext and len(post.selftext) > 50:
                results.append({
                    "title": post.title,
                    "excerpt": post.selftext[:180],
                    "url": f"https://reddit.com{post.permalink}",
                    "source": "Reddit"
                })

    return results[:25]  # hard limit for speed
