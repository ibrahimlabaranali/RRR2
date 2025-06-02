# Utility functions

import re
from textblob import TextBlob
from passlib.context import CryptContext
from fuzzywuzzy import fuzz

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------
# 🔐 PASSWORD UTILITIES
# --------------------------

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# --------------------------
# 📊 RISK TEXT CLASSIFIER
# --------------------------

def classify_risk_text(text: str) -> str:
    """
    Classify a risk type from text input using keywords and sentiment.
    Extendable to ML-based models in future.
    """
    try:
        text = text.lower()
        sentiment = TextBlob(text).sentiment.polarity

        # Rule-based keyword logic
        if any(term in text for term in ["armed", "robbery", "gun", "bandit", "attack", "kidnap", "terror"]):
            return "Security Risk"
        elif any(term in text for term in ["flood", "water", "washout", "rain", "submerged"]):
            return "Flood Risk"
        elif any(term in text for term in ["pothole", "bad road", "rough", "crater", "erosion"]):
            return "Road Condition"
        elif any(term in text for term in ["traffic", "hold-up", "jam", "gridlock", "checkpoint"]):
            return "Traffic"
        elif any(term in text for term in ["riot", "protest", "strike", "unrest"]):
            return "Civil Unrest"
        elif sentiment < -0.2:
            return "General Risk"
        else:
            return "Other"

    except Exception as e:
        print(f"❌ Risk classification failed: {e}")
        return "Unknown"


# --------------------------
# 📍 TEXT CLEANING & FUZZY LGA MATCHING
# --------------------------

def clean_text(text: str) -> str:
    """
    Normalize and clean user input text.
    """
    return re.sub(r"\s+", " ", text).strip().title()

def fuzzy_match_lga(input_lga: str, known_lgas: list) -> str:
    """
    Perform fuzzy matching of the given LGA against a list of known LGAs.
    Useful for fixing spelling issues.
    """
    max_score = 0
    best_match = input_lga
    for lga in known_lgas:
        score = fuzz.ratio(input_lga.lower(), lga.lower())
        if score > max_score:
            max_score = score
            best_match = lga
    return best_match
