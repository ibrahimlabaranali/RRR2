from pydantic import BaseModel
from datetime import datetime

class RiskReportCreate(BaseModel):
    reporter_name: str
    risk_type: str
    description: str
    location: str
    lga: str
    latitude: float
    longitude: float

class RiskReportOut(RiskReportCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
