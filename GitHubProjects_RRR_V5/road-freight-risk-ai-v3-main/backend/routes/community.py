# backend/routes/community.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
import os
import datetime
from datetime import timedelta
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()
router = APIRouter()

DB_PATH = os.getenv("REPORT_DB", "reports.db")

class CommunityVote(BaseModel):
    user_id: int
    report_id: int
    vote_type: str  # "confirm", "dispute", "neutral"
    location_lat: float
    location_lng: float
    timestamp: str
    device_id: str

class TrustScore(BaseModel):
    user_id: int
    score: float
    total_votes: int
    confirmed_reports: int
    disputed_reports: int
    last_updated: str

class SocialValidation(BaseModel):
    report_id: int
    platform: str  # "twitter", "facebook", "whatsapp"
    post_id: str
    engagement_count: int
    validation_status: str  # "pending", "verified", "rejected"

def init_community_db():
    """Initialize community validation tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Community votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_id INTEGER NOT NULL,
            vote_type TEXT NOT NULL,
            location_lat REAL,
            location_lng REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            device_id TEXT,
            ip_address TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (report_id) REFERENCES reports (id),
            UNIQUE(user_id, report_id)
        )
    ''')
    
    # Trust scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trust_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            score REAL DEFAULT 0.0,
            total_votes INTEGER DEFAULT 0,
            confirmed_reports INTEGER DEFAULT 0,
            disputed_reports INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Social validation table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_validations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            post_id TEXT NOT NULL,
            engagement_count INTEGER DEFAULT 0,
            validation_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified_at TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES reports (id)
        )
    ''')
    
    # Fake account detection logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fake_account_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            detection_type TEXT NOT NULL,
            confidence_score REAL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers"""
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def detect_fake_account(user_id: int, vote_data: CommunityVote) -> Dict:
    """Detect potential fake account activity"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for suspicious patterns
    suspicious_patterns = []
    confidence_score = 0.0
    
    # 1. Check for multiple votes from same location
    cursor.execute('''
        SELECT COUNT(*) FROM community_votes 
        WHERE user_id = ? AND location_lat = ? AND location_lng = ?
    ''', (user_id, vote_data.location_lat, vote_data.location_lng))
    
    same_location_votes = cursor.fetchone()[0]
    if same_location_votes > 3:
        suspicious_patterns.append("Multiple votes from same location")
        confidence_score += 0.3
    
    # 2. Check for rapid voting
    cursor.execute('''
        SELECT COUNT(*) FROM community_votes 
        WHERE user_id = ? AND timestamp > datetime('now', '-1 hour')
    ''', (user_id,))
    
    recent_votes = cursor.fetchone()[0]
    if recent_votes > 10:
        suspicious_patterns.append("Excessive voting in short time")
        confidence_score += 0.4
    
    # 3. Check for votes on reports far from user's location
    cursor.execute('''
        SELECT r.latitude, r.longitude FROM reports r
        WHERE r.id = ?
    ''', (vote_data.report_id,))
    
    report_location = cursor.fetchone()
    if report_location:
        distance = calculate_distance(
            vote_data.location_lat, vote_data.location_lng,
            report_location[0], report_location[1]
        )
        
        if distance > 50:  # More than 50km away
            suspicious_patterns.append("Voting on distant reports")
            confidence_score += 0.2
    
    # Log detection if suspicious
    if confidence_score > 0.3:
        cursor.execute('''
            INSERT INTO fake_account_logs (user_id, detection_type, confidence_score, details)
            VALUES (?, ?, ?, ?)
        ''', (user_id, "suspicious_voting", confidence_score, json.dumps(suspicious_patterns)))
        
        conn.commit()
    
    conn.close()
    
    return {
        "is_suspicious": confidence_score > 0.3,
        "confidence_score": confidence_score,
        "patterns": suspicious_patterns
    }

def update_trust_score(user_id: int):
    """Update user's trust score based on voting history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get voting statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_votes,
            SUM(CASE WHEN vote_type = 'confirm' THEN 1 ELSE 0 END) as confirms,
            SUM(CASE WHEN vote_type = 'dispute' THEN 1 ELSE 0 END) as disputes
        FROM community_votes 
        WHERE user_id = ? AND is_verified = TRUE
    ''', (user_id,))
    
    stats = cursor.fetchone()
    total_votes, confirms, disputes = stats
    
    if total_votes == 0:
        score = 0.0
    else:
        # Calculate trust score: (confirms - disputes) / total_votes
        score = max(0.0, min(1.0, (confirms - disputes) / total_votes))
    
    # Update or insert trust score
    cursor.execute('''
        INSERT OR REPLACE INTO trust_scores (user_id, score, total_votes, confirmed_reports, disputed_reports, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, score, total_votes, confirms, disputes, datetime.datetime.now()))
    
    conn.commit()
    conn.close()

@router.post("/vote")
def submit_community_vote(vote: CommunityVote):
    """Submit a community vote on a report"""
    try:
        init_community_db()
        
        # Detect fake account activity
        fake_detection = detect_fake_account(vote.user_id, vote)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already voted on this report
        cursor.execute('''
            SELECT id FROM community_votes 
            WHERE user_id = ? AND report_id = ?
        ''', (vote.user_id, vote.report_id))
        
        existing_vote = cursor.fetchone()
        if existing_vote:
            conn.close()
            raise HTTPException(status_code=400, detail="User already voted on this report")
        
        # Insert vote
        cursor.execute('''
            INSERT INTO community_votes (user_id, report_id, vote_type, location_lat, location_lng, device_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vote.user_id, vote.report_id, vote.vote_type, vote.location_lat, vote.location_lng, vote.device_id))
        
        # Mark as verified if no suspicious activity
        if not fake_detection["is_suspicious"]:
            cursor.execute('''
                UPDATE community_votes SET is_verified = TRUE 
                WHERE user_id = ? AND report_id = ?
            ''', (vote.user_id, vote.report_id))
        
        conn.commit()
        conn.close()
        
        # Update trust score
        update_trust_score(vote.user_id)
        
        return {
            "status": "success",
            "message": "Vote submitted successfully",
            "fake_detection": fake_detection
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vote submission failed: {str(e)}")

@router.get("/report-validations/{report_id}")
def get_report_validations(report_id: int):
    """Get all community validations for a specific report"""
    try:
        init_community_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get vote counts
        cursor.execute('''
            SELECT vote_type, COUNT(*) as count
            FROM community_votes 
            WHERE report_id = ? AND is_verified = TRUE
            GROUP BY vote_type
        ''', (report_id,))
        
        vote_counts = dict(cursor.fetchall())
        
        # Get trust index (average trust score of voters)
        cursor.execute('''
            SELECT AVG(ts.score) as avg_trust
            FROM community_votes cv
            JOIN trust_scores ts ON cv.user_id = ts.user_id
            WHERE cv.report_id = ? AND cv.is_verified = TRUE
        ''', (report_id,))
        
        avg_trust = cursor.fetchone()[0] or 0.0
        
        # Get social validations
        cursor.execute('''
            SELECT platform, engagement_count, validation_status
            FROM social_validations 
            WHERE report_id = ?
        ''', (report_id,))
        
        social_validations = [
            {
                "platform": row[0],
                "engagement_count": row[1],
                "validation_status": row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "status": "success",
            "report_id": report_id,
            "vote_counts": vote_counts,
            "trust_index": round(avg_trust, 2),
            "social_validations": social_validations,
            "total_votes": sum(vote_counts.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get validations: {str(e)}")

@router.post("/social-validation")
def add_social_validation(validation: SocialValidation):
    """Add social media validation for a report"""
    try:
        init_community_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO social_validations (report_id, platform, post_id, engagement_count, validation_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (validation.report_id, validation.platform, validation.post_id, 
              validation.engagement_count, validation.validation_status))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Social validation added successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add social validation: {str(e)}")

@router.get("/trust-score/{user_id}")
def get_user_trust_score(user_id: int):
    """Get user's trust score and statistics"""
    try:
        init_community_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT score, total_votes, confirmed_reports, disputed_reports, last_updated
            FROM trust_scores 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {
                "status": "success",
                "user_id": user_id,
                "trust_score": 0.0,
                "total_votes": 0,
                "confirmed_reports": 0,
                "disputed_reports": 0,
                "last_updated": None
            }
        
        return {
            "status": "success",
            "user_id": user_id,
            "trust_score": result[0],
            "total_votes": result[1],
            "confirmed_reports": result[2],
            "disputed_reports": result[3],
            "last_updated": result[4]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trust score: {str(e)}")

@router.get("/trending-reports")
def get_trending_reports():
    """Get reports with high community validation"""
    try:
        init_community_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.id, r.risk_type, r.location, 
                   COUNT(cv.id) as vote_count,
                   AVG(ts.score) as avg_trust
            FROM reports r
            LEFT JOIN community_votes cv ON r.id = cv.report_id AND cv.is_verified = TRUE
            LEFT JOIN trust_scores ts ON cv.user_id = ts.user_id
            WHERE r.timestamp > datetime('now', '-24 hours')
            GROUP BY r.id
            HAVING vote_count >= 3
            ORDER BY vote_count DESC, avg_trust DESC
            LIMIT 10
        ''')
        
        trending = [
            {
                "report_id": row[0],
                "risk_type": row[1],
                "location": row[2],
                "vote_count": row[3],
                "avg_trust": round(row[4] or 0.0, 2)
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "status": "success",
            "trending_reports": trending
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending reports: {str(e)}") 