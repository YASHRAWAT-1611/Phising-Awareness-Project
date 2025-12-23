import re

# Words that indicate urgency / threat
URGENT_PHRASES = [
    "within 30 minutes",
    "within 24 hours",
    "immediately",
    "last warning",
    "account will be blocked",
    "your account will be blocked",
    "will get frozen",
    "will be frozen",
]

# Asking for sensitive info
SENSITIVE_REQUESTS = [
    "otp",
    "one time password",
    "pin",
    "cvv",
    "password",
    "bank details",
    "card details",
]

# KYC / bank update patterns
KYC_PATTERNS = [
    "kyc has expired",
    "kyc is expired",
    "update your kyc",
    "verify your kyc",
    "kyc will be blocked",
]

# Lottery / prize scams
LOTTERY_PATTERNS = [
    "you have won",
    "you won",
    "lottery",
    "prize money",
    "claim your prize",
]

# Job + fee scams
JOB_FEE_PATTERNS = [
    "high salary job",
    "job in canada",
    "job abroad",
    "processing fee",
    "pay rs",
    "pay ₹",
    "pay rupees",
]

def text_rule_score(text: str) -> float:
    t = text.lower()
    score = 0.0

    # Strong red flags first
    if any(p in t for p in KYC_PATTERNS):
        score += 0.5
    if any(p in t for p in URGENT_PHRASES):
        score += 0.3
    if any(p in t for p in SENSITIVE_REQUESTS):
        score += 0.6
    if any(p in t for p in LOTTERY_PATTERNS):
        score += 0.5
    if any(p in t for p in JOB_FEE_PATTERNS):
        score += 0.5

    # Extra: presence of a URL in text often means higher risk
    if "http://" in t or "https://" in t:
        score += 0.2

    # Clamp score between 0 and 1
    return max(0.0, min(score, 1.0))


def url_rule_score(url: str) -> float:
    u = url.lower()
    score = 0.0

    # Suspicious patterns in phishing URLs
    if url.startswith("http://"):
        score += 0.3
    if u.count('.') > 3:
        score += 0.2
    if re.search(r"\d{2,}", u):
        score += 0.2

    # Common phishing words
    if any(w in u for w in ["verify", "update", "secure", "login", "kyc"]):
        score += 0.3

    # Bank/UPI brands + suspicious words
    brands = ["sbi", "hdfc", "icici", "axis", "paytm", "phonepe", "gpay", "upi"]
    if any(b in u for b in brands) and any(w in u for w in ["verify", "update", "kyc", "login"]):
        score += 0.3

    return max(0.0, min(score, 1.0))


def risk_from_score(score: float) -> str:
    # Make it stricter: HIGH starts from 0.6 now
    if score >= 0.6:
        return "HIGH"
    elif score >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"
