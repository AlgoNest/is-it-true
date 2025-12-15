CATEGORIES = {
    "Customer Support": ["support", "service", "agent", "help"],
    "Pricing & Billing": ["price", "billing", "charge", "fee", "refund"],
    "Quality Issues": ["broken", "defective", "poor", "quality", "stopped"],
    "Delivery Problems": ["delivery", "shipping", "late", "delay"],
    "Bugs & Errors": ["bug", "error", "crash", "glitch"]
}

def classify(text):
    text = text.lower()

    for category, keywords in CATEGORIES.items():
        if any(word in text for word in keywords):
            return category

    return "Other"
