from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
import os
import re
import whois
from datetime import datetime
import Levenshtein

# -------------------------------
# Load model
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = pickle.load(open(os.path.join(BASE_DIR, "ml/model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, "ml/vectorizer.pkl"), "rb"))

# -------------------------------
# FastAPI
# -------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Schema
# -------------------------------
class EmailData(BaseModel):
    subject: str
    sender: str
    body: str
    links: List[str]

# -------------------------------
# DOMAIN HELPERS
# -------------------------------

KNOWN_BRANDS = [
    "paypal.com", "google.com", "amazon.com",
    "microsoft.com", "apple.com", "facebook.com"
]

def get_base_domain(domain):
    parts = domain.split(".")
    return parts[-2] + "." + parts[-1] if len(parts) >= 2 else domain


def compute_spoof_score(domain):
    base = get_base_domain(domain)

    for brand in KNOWN_BRANDS:
        brand_base = get_base_domain(brand)

        similarity = Levenshtein.ratio(base, brand_base)

        if similarity > 0.8 and base != brand_base:
            return 0.7

    return 0


def get_domain_age(domain):
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:
            return (datetime.now() - creation_date).days
    except:
        pass

    return None

# -------------------------------
# LINK EXTRACTION
# -------------------------------

def extract_domains(text):
    pattern = r'(https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.(com|net|org|xyz|info|io)\b)'
    matches = re.findall(pattern, text)

    domains = []

    for match in matches:
        if isinstance(match, tuple):
            domains.append(match[0])
        else:
            domains.append(match)

    return domains

# -------------------------------
# FEATURE MODULES
# -------------------------------

def compute_content_score(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return prob, vec


def compute_sender_score(email):
    score = 0

    if "@" in email.sender:
        domain = email.sender.split("@")[-1].lower()

        age = get_domain_age(domain)
        if age:
            if age < 30:
                score += 0.6
            elif age < 180:
                score += 0.3
            else:
                score -= 0.2

        score += compute_spoof_score(domain)

    return max(0, min(score, 1))


def compute_link_score(email, text):
    links = email.links or []
    links += extract_domains(text)

    if not links:
        return 0

    score = 0.2 + 0.1 * len(links)

    for link in links:
        domain = link

        if "://" in link:
            domain = link.split("/")[2]

        domain = domain.replace("www.", "")

        age = get_domain_age(domain)
        if age:
            if age < 30:
                score += 0.5
            elif age < 180:
                score += 0.2

        score += compute_spoof_score(domain)

    return min(score, 1)


def compute_context_score(text_lower):
    score = 0

    if "click" in text_lower and "link" in text_lower:
        score += 0.3

    if "verify" in text_lower and "account" in text_lower:
        score += 0.3

    if "win" in text_lower and "prize" in text_lower:
        score += 0.5

    if "urgent" in text_lower:
        score += 0.2

    return min(score, 1)

# -------------------------------
# ADAPTIVE + CONFLICT-AWARE SYSTEM
# -------------------------------

def compute_final_score(content, sender, link, context):

    reasons = []

    # -------------------------------
    # Adaptive weights
    # -------------------------------
    w_content = 0.3 + 0.3 * content
    w_context = 0.2 + 0.2 * context
    w_link = 0.2 + 0.1 * link
    w_sender = max(0.1, 1 - (w_content + w_context + w_link))

    total = w_content + w_sender + w_link + w_context

    w_content /= total
    w_sender /= total
    w_link /= total
    w_context /= total

    score = (
        w_content * content +
        w_sender * sender +
        w_link * link +
        w_context * context
    )

    # -------------------------------
    # CONFLICT DETECTION
    # -------------------------------
    conflict = 0

    if content > 0.8 and link < 0.2 and context < 0.2:
        conflict += 1
        reasons.append("Suspicious content but no supporting links or actions")

    if content > 0.8 and sender < 0.2:
        conflict += 1
        reasons.append("Suspicious content but sender appears trusted")

    if link > 0.5 and content < 0.4:
        conflict += 1
        reasons.append("Suspicious links but content looks normal")

    # -------------------------------
    # CONFIDENCE ADJUSTMENT
    # -------------------------------
    if conflict == 1:
        score *= 0.9
    elif conflict >= 2:
        score *= 0.75

    return max(0, min(score, 1)), reasons


def classify(score):
    if score > 0.75:
        return "danger"
    elif score > 0.45:
        return "warning"
    return "safe"

# -------------------------------
# API
# -------------------------------

@app.post("/analyze-email")
def analyze_email(email: EmailData):

    text = f"{email.subject} {email.body}"
    text_lower = text.lower()

    content_score, vec = compute_content_score(text)
    sender_score = compute_sender_score(email)
    link_score = compute_link_score(email, text)
    context_score = compute_context_score(text_lower)

    final_score, conflict_reasons = compute_final_score(
        content_score,
        sender_score,
        link_score,
        context_score
    )

    level = classify(final_score)

    # explainability
    feature_names = vectorizer.get_feature_names_out()
    vec_array = vec.toarray()[0]

    top_indices = vec_array.argsort()[-5:]
    important_words = [feature_names[i] for i in top_indices]

    signals = {
        "content": [
            f"ML score: {round(content_score, 2)}",
            "Top indicators: " + ", ".join(important_words)
        ],
        "sender": [f"Sender score: {round(sender_score, 2)}"],
        "links": [f"Link score: {round(link_score, 2)}"],
        "context": [f"Context score: {round(context_score, 2)}"],
        "conflict": conflict_reasons
    }

    print("=== FINAL INTELLIGENT SYSTEM ===")
    print("Content:", content_score)
    print("Sender:", sender_score)
    print("Link:", link_score)
    print("Context:", context_score)
    print("Final:", final_score)
    print("Level:", level)
    print("Conflict Reasons:", conflict_reasons)

    return {
        "confidence": round(float(final_score), 2),
        "level": level,
        "signals": signals
    }