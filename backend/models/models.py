from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base
import datetime

class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_name = Column(String)
    risk_type = Column(String)
    description = Column(String)
    location = Column(String)
    lga = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
