# backend/routes/advice.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

DB_PATH = os.getenv("REPORT_DB", "reports.db")


class AdviceRequest(BaseModel):
    risk_type: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    time_of_day: Optional[str] = None


class SafetyAdvice(BaseModel):
    risk_type: str
    advice: str
    severity: str
    confirmations: int
    last_updated: str


# Context-aware safety advice templates
SAFETY_ADVICE_TEMPLATES = {
    "Armed Robbery": {
        "high": [
            "🚨 CRITICAL: Avoid this route immediately. Armed robbery reported.",
            "🛡️ Use alternative routes and travel in convoy if possible.",
            "📱 Contact local authorities and report suspicious activity.",
            "⏰ Avoid travel during early morning (4-6 AM) and late evening (8-10 PM)."
        ],
        "medium": [
            "⚠️ Exercise extreme caution. Recent robbery reports in this area.",
            "🛡️ Travel with others and avoid isolated stretches.",
            "📱 Keep emergency contacts readily available.",
            "⏰ Consider alternative routes during peak risk hours."
        ]
    },
    "Banditry": {
        "high": [
            "🚨 CRITICAL: Bandit activity confirmed in this area.",
            "🛡️ Avoid travel until security forces clear the area.",
            "📱 Contact local security agencies for updates.",
            "⏰ Do not travel during night hours (6 PM - 6 AM)."
        ],
        "medium": [
            "⚠️ Bandit activity reported. Travel with extreme caution.",
            "🛡️ Use main highways and avoid bush paths.",
            "📱 Travel in groups and maintain communication.",
            "⏰ Avoid isolated areas during early morning and late evening."
        ]
    },
    "Flooding": {
        "high": [
            "🌊 CRITICAL: Severe flooding reported. Route impassable.",
            "🛡️ Do not attempt to cross flooded areas.",
            "📱 Monitor weather updates and water levels.",
            "⏰ Wait for water to recede before attempting travel."
        ],
        "medium": [
            "🌊 Moderate flooding. Exercise caution when crossing.",
            "🛡️ Check water depth before crossing.",
            "📱 Use alternative routes if available.",
            "⏰ Avoid travel during heavy rainfall."
        ]
    },
    "Protest": {
        "high": [
            "📢 CRITICAL: Active protest/riot in progress.",
            "🛡️ Avoid the area completely. Use alternative routes.",
            "📱 Monitor local news for updates.",
            "⏰ Expect delays and road closures."
        ],
        "medium": [
            "📢 Protest activity reported. Expect delays.",
            "🛡️ Use alternative routes if possible.",
            "📱 Stay informed about protest developments.",
            "⏰ Allow extra travel time."
        ]
    },
    "Road Closure": {
        "high": [
            "🚧 CRITICAL: Road completely blocked or closed.",
            "🛡️ Use alternative routes immediately.",
            "📱 Check with local authorities for reopening time.",
            "⏰ Expect significant delays."
        ],
        "medium": [
            "🚧 Road partially blocked. Expect delays.",
            "🛡️ Use alternative routes if available.",
            "📱 Monitor for updates on road conditions.",
            "⏰ Allow extra travel time."
        ]
    },
    "Accident": {
        "high": [
            "🚗 CRITICAL: Major accident blocking traffic.",
            "🛡️ Use alternative routes to avoid congestion.",
            "📱 Emergency services are on scene.",
            "⏰ Expect significant delays."
        ],
        "medium": [
            "🚗 Accident reported. Expect minor delays.",
            "🛡️ Drive carefully and follow traffic instructions.",
            "📱 Emergency services are responding.",
            "⏰ Allow extra travel time."
        ]
    },
    "Kidnap": {
        "high": [
            "🚨 CRITICAL: Kidnapping incidents reported in this area.",
            "🛡️ Avoid travel until security situation improves.",
            "📱 Contact security agencies for guidance.",
            "⏰ Do not travel alone or during night hours."
        ],
        "medium": [
            "⚠️ Kidnapping risk reported. Travel with extreme caution.",
            "🛡️ Travel in groups and avoid isolated areas.",
            "📱 Keep emergency contacts readily available.",
            "⏰ Avoid travel during early morning and late evening."
        ]
    }
}


def get_risk_severity(risk_type: str, confirmations: int, recent_reports: int) -> str:
    """Determine risk severity based on confirmations and recent reports"""
    if confirmations >= 5 or recent_reports >= 3:
        return "high"
    elif confirmations >= 2 or recent_reports >= 2:
        return "medium"
    else:
        return "low"


def get_recent_reports_count(risk_type: str, location: str, hours: int = 24) -> int:
    """Get count of recent reports for the same risk type and location"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get reports from the last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT COUNT(*) FROM reports 
            WHERE risk_type = ? 
            AND location LIKE ? 
            AND timestamp > ?
        """, (risk_type, f"%{location}%", cutoff_time.isoformat()))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting recent reports: {e}")
        return 0


def get_confirmations_count(risk_type: str, location: str) -> int:
    """Get count of confirmations from other drivers"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM confirmations 
            WHERE risk_type = ? 
            AND location LIKE ?
        """, (risk_type, f"%{location}%"))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting confirmations: {e}")
        return 0


def generate_time_specific_advice(risk_type: str, time_of_day: str) -> str:
    """Generate time-specific advice based on risk type and time"""
    time_advice = {
        "Armed Robbery": {
            "morning": "⏰ Early morning (4-6 AM) is high-risk period. Avoid travel during these hours.",
            "evening": "⏰ Evening hours (6-10 PM) are high-risk. Use alternative routes.",
            "night": "⏰ Night travel is extremely dangerous. Avoid completely.",
            "day": "⏰ Daytime travel is safer but remain vigilant."
        },
        "Banditry": {
            "morning": "⏰ Early morning is high-risk for bandit activity.",
            "evening": "⏰ Evening hours are dangerous. Travel in convoy if necessary.",
            "night": "⏰ Night travel is prohibited due to bandit risk.",
            "day": "⏰ Daytime travel is recommended with caution."
        },
        "Flooding": {
            "morning": "⏰ Morning hours may have receding water levels.",
            "evening": "⏰ Evening may bring additional rainfall.",
            "night": "⏰ Night travel dangerous due to poor visibility.",
            "day": "⏰ Daytime allows better assessment of conditions."
        }
    }
    
    return time_advice.get(risk_type, {}).get(time_of_day, "")


@router.post("/generate")
def generate_safety_advice(request: AdviceRequest):
    """Generate context-aware safety advice"""
    try:
        # Get recent reports and confirmations
        recent_reports = get_recent_reports_count(request.risk_type, request.location)
        confirmations = get_confirmations_count(request.risk_type, request.location)
        
        # Determine severity
        severity = get_risk_severity(request.risk_type, confirmations, recent_reports)
        
        # Get base advice from templates
        if request.risk_type in SAFETY_ADVICE_TEMPLATES:
            base_advice = SAFETY_ADVICE_TEMPLATES[request.risk_type].get(severity, [])
        else:
            base_advice = [
                "⚠️ Risk reported in this area. Exercise caution.",
                "🛡️ Use alternative routes if available.",
                "📱 Stay informed about local conditions.",
                "⏰ Allow extra travel time."
            ]
        
        # Combine advice
        combined_advice = base_advice.copy()
        
        # Add time-specific advice if available
        if request.time_of_day:
            time_advice = generate_time_specific_advice(request.risk_type, request.time_of_day)
            if time_advice:
                combined_advice.append(time_advice)
        
        # Add confirmation context
        if confirmations > 0:
            combined_advice.append(f"✅ Confirmed by {confirmations} other drivers")
        
        if recent_reports > 0:
            combined_advice.append(f"📊 {recent_reports} recent reports in this area")
        
        # Join advice into a single string
        advice_text = "\n".join(combined_advice)
        
        return SafetyAdvice(
            risk_type=request.risk_type,
            advice=advice_text,
            severity=severity,
            confirmations=confirmations,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advice: {str(e)}")


@router.post("/confirm")
def confirm_risk(risk_type: str, location: str, user_id: int):
    """Allow users to confirm a risk report"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create confirmations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confirmations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                risk_type TEXT,
                location TEXT,
                confirmed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if user already confirmed this risk
        cursor.execute("""
            SELECT id FROM confirmations 
            WHERE user_id = ? AND risk_type = ? AND location LIKE ?
        """, (user_id, risk_type, f"%{location}%"))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="You have already confirmed this risk")
        
        # Add confirmation
        cursor.execute("""
            INSERT INTO confirmations (user_id, risk_type, location)
            VALUES (?, ?, ?)
        """, (user_id, risk_type, location))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "✅ Risk confirmed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirming risk: {str(e)}")


@router.get("/confirmations/{risk_type}")
def get_risk_confirmations(risk_type: str, location: str):
    """Get confirmation count for a specific risk"""
    try:
        confirmations = get_confirmations_count(risk_type, location)
        recent_reports = get_recent_reports_count(risk_type, location)
        
        return {
            "risk_type": risk_type,
            "location": location,
            "confirmations": confirmations,
            "recent_reports": recent_reports,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting confirmations: {str(e)}")


@router.get("/trending")
def get_trending_risks():
    """Get trending risks based on recent reports and confirmations"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get risks with most confirmations in the last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        cursor.execute("""
            SELECT risk_type, location, COUNT(*) as confirmations
            FROM confirmations 
            WHERE confirmed_at > ?
            GROUP BY risk_type, location
            ORDER BY confirmations DESC
            LIMIT 10
        """, (cutoff_time.isoformat(),))
        
        trending = cursor.fetchall()
        conn.close()
        
        return {
            "trending_risks": [
                {
                    "risk_type": row[0],
                    "location": row[1],
                    "confirmations": row[2]
                }
                for row in trending
            ],
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trending risks: {str(e)}") 