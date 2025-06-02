from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional

from backend.database import get_db
from backend.models import Report, User
from backend.schemas import ReportCreate, ReportResponse
from backend.routes.auth import get_current_user  # Ensure JWT is used

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# 📌 Submit a new risk report
@router.post("/", response_model=ReportResponse)
def submit_report(report: ReportCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["id"] != report.user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="You can only submit your own reports.")

    user = db.query(User).filter(User.id == report.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 🚫 Prevent duplicate reports within 10 minutes at same location
    recent_duplicate = db.query(Report).filter(
        Report.user_id == report.user_id,
        Report.location == report.location,
        Report.description == report.description,
        Report.timestamp > datetime.utcnow() - timedelta(minutes=10)
    ).first()
    if recent_duplicate:
        raise HTTPException(status_code=409, detail="Duplicate report recently submitted.")

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

# 📋 Get all reports (Admin only)
@router.get("/", response_model=List[ReportResponse])
def get_reports(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access all reports.")
    return db.query(Report).order_by(Report.timestamp.desc()).offset(offset).limit(limit).all()

# 📍 Get reports by state/LGA with pagination
@router.get("/filter", response_model=List[ReportResponse])
def filter_reports(
    state: Optional[str] = None,
    lga: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Report)

    if state and lga:
        query = query.filter(and_(Report.state == state, Report.lga == lga))
    elif state:
        query = query.filter(Report.state == state)
    elif lga:
        query = query.filter(Report.lga == lga)

    # Restrict non-admins to their own reports
    if current_user["role"] != "admin":
        query = query.filter(Report.user_id == current_user["id"])

    return query.order_by(Report.timestamp.desc()).offset(offset).limit(limit).all()

# 🕓 Get reports in last X days
@router.get("/recent", response_model=List[ReportResponse])
def get_recent_reports(
    days: int = Query(default=1, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    threshold = datetime.utcnow() - timedelta(days=days)
    query = db.query(Report).filter(Report.timestamp >= threshold)

    if current_user["role"] != "admin":
        query = query.filter(Report.user_id == current_user["id"])

    return query.order_by(Report.timestamp.desc()).all()
