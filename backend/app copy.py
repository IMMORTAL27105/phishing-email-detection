from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle

# -------------------------------
# Load ML model and vectorizer
# -------------------------------
model = pickle.load(open("ml/model.pkl", "rb"))
vectorizer = pickle.load(open("ml/vectorizer.pkl", "rb"))

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI()

# CORS (required for Chrome extension)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Request schema
# -------------------------------
class EmailData(BaseModel):
    subject: str
    sender: str
    body: str
    links: List[str]

# -------------------------------
# API endpoint
# -------------------------------
@app.post("/analyze-email")
def analyze_email(email: EmailData):
    text = f"{email.subject} {email.body}"

    # ML prediction
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]  # phishing probability

    # Explainability signals
    signals = {
        "content": [],
        "sender": [],
        "links": []
    }

    if "urgent" in text.lower():
        signals["content"].append("Urgent language")

    if "certificate" in text.lower():
        signals["content"].append("Certificate scam pattern")

    if email.sender.endswith("@gmail.com"):
        signals["sender"].append("Free email provider")

    if email.links:
        signals["links"].append("Contains external links")

    # Risk level
    if prob > 0.7:
        level = "danger"
    elif prob > 0.4:
        level = "warning"
    else:
        level = "safe"

    return {
    return {
        "confidence": round(float(prob), 2),
        "level": level,
        "signals": signals,
        "summary": (
            "This email matches known phishing patterns."
            if level != "safe"
            else "No strong phishing indicators detected."
        )
    }