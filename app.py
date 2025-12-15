from flask import Flask, render_template, request
from services.search_api import search_complaints
from services.classify import classify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q")
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

    return render_template(
        "index.html",
        query=query,
        complaints=complaints
    )

if __name__ == "__main__":
    app.run(debug=True)
