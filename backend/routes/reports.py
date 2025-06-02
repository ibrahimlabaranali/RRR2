from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Report, User
from backend.schemas import ReportCreate, ReportResponse
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# 📌 Submit a new risk report
@router.post("/", response_model=ReportResponse)
def submit_report(report: ReportCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == report.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    new_report = Report(
        user_id=report.user_id,
        risk_type=report.risk_type,
        description=report.description,
        location=report.location,
        state=report.state,
        lga=report.lga,
        lat=report.lat,
        lon=report.lon,
        timestamp=datetime.utcnow()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

# 📋 Get all reports
@router.get("/", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.timestamp.desc()).all()

# 📍 Get reports by state or LGA
@router.get("/filter", response_model=List[ReportResponse])
def filter_reports(state: str = None, lga: str = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    if state:
        query = query.filter(Report.state == state)
    if lga:
        query = query.filter(Report.lga == lga)
    return query.order_by(Report.timestamp.desc()).all()
