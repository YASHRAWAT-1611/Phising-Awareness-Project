import re

URGENT_WORDS = [
    "immediately", "within 30 minutes", "last warning",
    "account will be blocked", "urgent", "verify now"
]
SENSITIVE_REQUESTS = [
    "otp", "one time password", "pin", "cvv", "password", "bank details"
]

def text_rule_score(text: str) -> float:
    text_lower = text.lower()
    score = 0.0
    for w in URGENT_WORDS:
        if w in text_lower:
            score += 0.2
    for w in SENSITIVE_REQUESTS:
        if w in text_lower:
            score += 0.3
    return min(score, 1.0)

def url_rule_score(url: str) -> float:
    score = 0.0
    if url.startswith("http://"):  # no https
        score += 0.2
    if re.search(r"\d{2,}", url):  # lots of numbers
        score += 0.2
    if url.count('.') > 3:  # many subdomains
        score += 0.2
    if any(word in url.lower() for word in ["verify", "secure", "update", "login"]):
        score += 0.2
    return min(score, 1.0)

def risk_from_score(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    elif score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"
