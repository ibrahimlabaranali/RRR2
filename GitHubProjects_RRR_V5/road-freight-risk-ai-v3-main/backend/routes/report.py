# backend/routes/report.py
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pydantic import BaseModel, validator
import sqlite3
import os
import datetime
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
DB_PATH = os.getenv("REPORT_DB", "reports.db")
API_BASE = os.getenv("API_URL", "http://localhost:8000")

# File upload constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/m4a", "audio/mp3"]


class Report(BaseModel):
    username: str
    risk_type: str
    latitude: float
    longitude: float
    location: str
    description: Optional[str] = None
    timestamp: str = str(datetime.datetime.now())
    
    @validator('risk_type')
    def validate_risk_type(cls, v):
        valid_types = [
            "Flooding", "Armed Robbery", "Banditry", "Protest", 
            "Road Closure", "Accident", "Kidnap", "Other"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid risk type. Must be one of: {valid_types}")
        return v
    
    @validator('description')
    def validate_description(cls, v, values):
        if values.get('risk_type') == 'Other' and not v:
            raise ValueError("Description is required when risk type is 'Other'")
        return v


class ReportSubmission(BaseModel):
    username: str
    risk_type: str
    latitude: float
    longitude: float
    location: str
    description: Optional[str] = None
    confirmed: bool = False


def validate_file_upload(file: UploadFile) -> bool:
    """Validate file upload size and type"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
    
    if file.content_type not in ALLOWED_IMAGE_TYPES + ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, MP3, WAV, M4A"
        )
    
    return True


def save_uploaded_file(file: UploadFile, report_id: int) -> str:
    """Save uploaded file and return file path"""
    upload_dir = "uploads/reports"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = file.filename.split(".")[-1] if file.filename else "bin"
    file_path = f"{upload_dir}/{report_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
    
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return file_path


def generate_safety_advice_for_report(report: Report) -> dict:
    """Generate safety advice for the submitted report"""
    try:
        advice_request = {
            "risk_type": report.risk_type,
            "location": report.location,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "description": report.description,
            "time_of_day": get_time_of_day()
        }
        
        response = requests.post(f"{API_BASE}/advice/generate", json=advice_request)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "advice": "⚠️ Our team will verify and update advice shortly.",
                "severity": "low",
                "confirmations": 0
            }
    except Exception as e:
        print(f"Error generating advice: {e}")
        return {
            "advice": "⚠️ Our team will verify and update advice shortly.",
            "severity": "low",
            "confirmations": 0
        }


def get_time_of_day() -> str:
    """Get current time of day category"""
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "day"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"


@router.post("/submit")
def submit_report(report: ReportSubmission):
    """Submit a road risk report with confirmation"""
    if not report.confirmed:
        raise HTTPException(status_code=400, detail="Report must be confirmed before submission")
    
    # Validate required fields
    if not report.risk_type or not report.location:
        raise HTTPException(status_code=400, detail="Risk type and location are required")
    
    if report.risk_type == "Other" and not report.description:
        raise HTTPException(status_code=400, detail="Description is required when risk type is 'Other'")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create enhanced reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                risk_type TEXT,
                latitude REAL,
                longitude REAL,
                location TEXT,
                description TEXT,
                timestamp TEXT,
                advice TEXT,
                severity TEXT,
                confirmations INTEGER DEFAULT 0,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Generate safety advice
        advice_data = generate_safety_advice_for_report(Report(**report.dict()))
        
        # Insert report
        cursor.execute("""
            INSERT INTO reports (
                username, risk_type, latitude, longitude, location, 
                description, timestamp, advice, severity, confirmations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.username, report.risk_type, report.latitude, 
            report.longitude, report.location, report.description,
            report.timestamp, advice_data.get("advice", ""),
            advice_data.get("severity", "low"), advice_data.get("confirmations", 0)
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "message": "✅ Report submitted successfully",
            "report_id": report_id,
            "advice": advice_data.get("advice", ""),
            "severity": advice_data.get("severity", "low"),
            "confirmations": advice_data.get("confirmations", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting report: {str(e)}")


@router.post("/submit-with-file")
async def submit_report_with_file(
    username: str = Form(...),
    risk_type: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location: str = Form(...),
    description: Optional[str] = Form(None),
    confirmed: bool = Form(False),
    file: Optional[UploadFile] = File(None)
):
    """Submit report with optional file upload"""
    if not confirmed:
        raise HTTPException(status_code=400, detail="Report must be confirmed before submission")
    
    # Validate file if provided
    file_path = None
    if file:
        validate_file_upload(file)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create enhanced reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                risk_type TEXT,
                latitude REAL,
                longitude REAL,
                location TEXT,
                description TEXT,
                timestamp TEXT,
                advice TEXT,
                severity TEXT,
                confirmations INTEGER DEFAULT 0,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Generate safety advice
        advice_request = {
            "risk_type": risk_type,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "time_of_day": get_time_of_day()
        }
        
        advice_data = generate_safety_advice_for_report(Report(
            username=username,
            risk_type=risk_type,
            latitude=latitude,
            longitude=longitude,
            location=location,
            description=description
        ))
        
        # Insert report
        cursor.execute("""
            INSERT INTO reports (
                username, risk_type, latitude, longitude, location, 
                description, timestamp, advice, severity, confirmations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, risk_type, latitude, longitude, location,
            description, str(datetime.datetime.now()),
            advice_data.get("advice", ""), advice_data.get("severity", "low"),
            advice_data.get("confirmations", 0)
        ))
        
        report_id = cursor.lastrowid
        
        # Save file if provided
        if file:
            file_path = save_uploaded_file(file, report_id)
            cursor.execute("UPDATE reports SET file_path = ? WHERE id = ?", (file_path, report_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "✅ Report submitted successfully",
            "report_id": report_id,
            "advice": advice_data.get("advice", ""),
            "severity": advice_data.get("severity", "low"),
            "confirmations": advice_data.get("confirmations", 0),
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting report: {str(e)}")


@router.get("/all")
def get_all_reports():
    """Get all reports with enhanced data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, risk_type, latitude, longitude, location, 
                   description, timestamp, advice, severity, confirmations, file_path
            FROM reports 
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "username": row[1],
                "risk_type": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "location": row[5],
                "description": row[6],
                "timestamp": row[7],
                "advice": row[8],
                "severity": row[9],
                "confirmations": row[10],
                "file_path": row[11]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")


@router.get("/user/{username}")
def get_user_reports(username: str):
    """Get reports for a specific user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, risk_type, latitude, longitude, location, 
                   description, timestamp, advice, severity, confirmations
            FROM reports 
            WHERE username = ?
            ORDER BY timestamp DESC
        """, (username,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "risk_type": row[1],
                "latitude": row[2],
                "longitude": row[3],
                "location": row[4],
                "description": row[5],
                "timestamp": row[6],
                "advice": row[7],
                "severity": row[8],
                "confirmations": row[9]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user reports: {str(e)}")


@router.get("/{report_id}")
def get_report_by_id(report_id: int):
    """Get a specific report by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, risk_type, latitude, longitude, location, 
                   description, timestamp, advice, severity, confirmations, file_path
            FROM reports 
            WHERE id = ?
        """, (report_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "id": row[0],
            "username": row[1],
            "risk_type": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "location": row[5],
            "description": row[6],
            "timestamp": row[7],
            "advice": row[8],
            "severity": row[9],
            "confirmations": row[10],
            "file_path": row[11]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")


@router.delete("/{report_id}")
def delete_report(report_id: int, username: str):
    """Delete a report (only by the user who created it or admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if report exists and user has permission
        cursor.execute("SELECT username FROM reports WHERE id = ?", (report_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if result[0] != username:
            raise HTTPException(status_code=403, detail="You can only delete your own reports")
        
        # Delete the report
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "✅ Report deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")
