# backend/routes/classify.py
from fastapi import APIRouter
from pydantic import BaseModel
from textblob import TextBlob

router = APIRouter()


class TextInput(BaseModel):
    text: str


keywords = {
    "flood": "Flooding",
    "water": "Flooding",
    "attack": "Armed Robbery",
    "gun": "Banditry",
    "riot": "Protest",
    "strike": "Protest",
    "roadblock": "Road Closure",
    "accident": "Accident"
}


@router.post("/text")
def classify_text(input: TextInput):
    text = input.text.lower()
    for key in keywords:
        if key in text:
            return {"risk_type": keywords[key]}
    polarity = TextBlob(text).sentiment.polarity
    if polarity < -0.5:
        return {"risk_type": "Severe Alert"}
    return {"risk_type": "Other/Unknown"}
