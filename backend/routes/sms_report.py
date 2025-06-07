from fastapi import APIRouter, Request
from pydantic import BaseModel
from backend.db import insert_report  # adjust based on your structure

router = APIRouter()

class SMSReport(BaseModel):
    message: str  # Example: "Risk: Banditry; Loc: Faskari-Kaura Rd; State: Katsina; LGA: Faskari; Lat:10.24; Lon:7.31"

@router.post("/sms/")
async def receive_sms(report: SMSReport):
    try:
        data = {}
        parts = report.message.split(";")
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                data[key.strip().lower()] = value.strip()

        report_data = {
            "user_id": 0,
            "risk_type": data.get("risk", "Other"),
            "description": "Reported via SMS",
            "location": data.get("loc", "Unknown"),
            "state": data.get("state", "Unknown"),
            "lga": data.get("lga", "Unknown"),
            "lat": float(data.get("lat", 0.0)),
            "lon": float(data.get("lon", 0.0))
        }

        insert_report(report_data)
        return {"status": "Report received via SMS", "data": report_data}

    except Exception as e:
        return {"error": str(e)}
