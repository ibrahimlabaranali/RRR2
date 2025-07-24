from fastapi import APIRouter
from textblob import TextBlob
from pydantic import BaseModel

router = APIRouter(prefix="/classify", tags=["Classifier"])

# 🔍 Define input model
class ClassificationInput(BaseModel):
    description: str

# 🤖 POST endpoint
@router.post("/")
def classify_text(data: ClassificationInput):
    text = data.description
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    # Rule-based risk classification
    text_lower = text.lower()

    if any(term in text_lower for term in ["bandit", "gun", "kidnap", "attack"]):
        risk_type = "Banditry"
    elif any(term in text_lower for term in ["flood", "rain", "submerged"]):
        risk_type = "Flooding"
    elif any(term in text_lower for term in ["protest", "riot", "strike"]):
        risk_type = "Protest"
    elif any(term in text_lower for term in ["robbery", "theft", "armed"]):
        risk_type = "Robbery"
    elif polarity < -0.3:
        risk_type = "Tense Situation"
    else:
        risk_type = "General Road Hazard"

    return {
        "risk_type": risk_type,
        "polarity_score": round(polarity, 3),
        "original_text": text
    }
