from flask import Flask, render_template, request
from services.search_api import search_complaints
from services.classify import classify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        complaints = []

        if query:
            raw_results = search_complaints(query)

            for r in raw_results:
                category = classify(r["title"] + " " + r["excerpt"])
                complaints.append({
                    "title": r["title"],
                    "excerpt": r["excerpt"],
                    "url": r["url"],
                    "source": r["source"],
                    "category": category
                })

            # Sort for Jinja groupby
            complaints.sort(key=lambda x: x["category"])

            # Render results after POST
            return render_template(
                "index.html",
                query=query,
                complaints=complaints
            )

    # For GET request, render only the empty search page
    return render_template(
        "index.html"
    )
