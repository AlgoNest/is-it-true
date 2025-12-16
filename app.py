from flask import Flask, render_template, request
from services.search_api import search_complaints
from services.classify import classify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query").strip()
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

            complaints.sort(key=lambda x: x["category"])

            return render_template(
                "index.html",
                query=query,
                complaints=complaints
            )

    return render_template("index.html")

