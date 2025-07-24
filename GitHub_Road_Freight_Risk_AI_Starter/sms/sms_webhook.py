from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

FASTAPI_ENDPOINT = "https://road-freight-risk-ai.onrender.com/reports/"

def classify_sms(text):
    text_lower = text.lower()
    if "robbery" in text_lower or "gun" in text_lower:
        return "Armed Robbery"
    elif "flood" in text_lower or "rain" in text_lower:
        return "Flooding"
    elif "accident" in text_lower or "crash" in text_lower:
        return "Accident"
    elif "bandit" in text_lower:
        return "Banditry"
    elif "protest" in text_lower:
        return "Protest"
    elif "checkpoint" in text_lower:
        return "Checkpoint Delay"
    else:
        return "Other"

DEFAULT_LAT = 10.5
DEFAULT_LON = 7.4

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body', '').strip()
    sender = request.form.get('From', '').strip()

    risk_type = classify_sms(incoming_msg)
    lga = "Unknown"
    state = "Unknown"
    location = "Unknown"

    payload = {
        "user_id": 999,
        "risk_type": risk_type,
        "description": incoming_msg,
        "location": location,
        "state": state,
        "lga": lga,
        "lat": DEFAULT_LAT,
        "lon": DEFAULT_LON
    }

    try:
        response = requests.post(FASTAPI_ENDPOINT, json=payload)
        if response.status_code == 200:
            reply = f"✅ SMS received. Your report was logged as '{risk_type}'. Stay safe."
        else:
            reply = f"⚠️ Received SMS but failed to log report. Try again later."
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

