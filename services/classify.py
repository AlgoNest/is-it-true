import re

CATEGORIES = {
    "Customer Support": [
        "support", "customer service", "agent", "help",
        "no response", "not responding", "rude", "unhelpful"
    ],
    "Pricing & Billing": [
        "price", "pricing", "billing", "charge", "charged",
        "fee", "refund", "money", "payment", "subscription",
        "auto renewal", "deducted", "overcharged"
    ],
    "Quality Issues": [
        "broken", "defective", "poor", "quality", "stopped",
        "not working", "damaged", "faulty", "low quality"
    ],
    "Delivery Problems": [
        "delivery", "shipping", "late", "delay",
        "not delivered", "missing", "courier", "tracking"
    ],
    "Bugs & Errors": [
        "bug", "error", "crash", "glitch",
        "not opening", "login issue", "failed", "loading",
        "app issue", "website issue"
    ],
    "Scam & Fraud": [
        "scam", "fraud", "fake", "cheat",
        "stolen", "hacked", "unauthorized", "phishing"
    ]
}

# ------------------------

def classify(text):
    if not text:
        return "Other"

    text = text.lower()

    # Normalize common phrases
    text = re.sub(r"\s+", " ", text)

    scores = {}

    for category, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        if score > 0:
            scores[category] = score

    # Return the strongest match
    if scores:
        return max(scores, key=scores.get)

    # Intent-based fallback (non-technical users)
    if any(word in text for word in ["problem", "issue", "complaint", "bad", "worst"]):
        return "General Complaint"

    if any(word in text for word in ["review", "experience", "feedback"]):
        return "User Experience"

    return "Other"
