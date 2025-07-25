# backend/routes/offline.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import json
import datetime
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

DB_PATH = os.getenv("REPORT_DB", "reports.db")
OFFLINE_CACHE_DIR = "offline_cache"
os.makedirs(OFFLINE_CACHE_DIR, exist_ok=True)

class OfflineReport(BaseModel):
    user_id: int
    risk_type: str
    latitude: float
    longitude: float
    location: str
    description: Optional[str] = None
    timestamp: str
    device_id: str
    sync_status: str = "pending"

class SyncRequest(BaseModel):
    user_id: int
    device_id: str
    reports: List[OfflineReport]

class SyncResponse(BaseModel):
    synced_reports: int
    failed_reports: int
    errors: List[str] = []

def save_offline_report(report: OfflineReport) -> bool:
    """Save report to offline cache"""
    try:
        cache_file = os.path.join(OFFLINE_CACHE_DIR, f"user_{report.user_id}_device_{report.device_id}.json")
        
        # Load existing cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        else:
            cache = {"reports": []}
        
        # Add new report
        cache["reports"].append(report.dict())
        
        # Save back to cache
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving offline report: {e}")
        return False

def get_offline_reports(user_id: int, device_id: str) -> List[OfflineReport]:
    """Get all offline reports for a user/device"""
    try:
        cache_file = os.path.join(OFFLINE_CACHE_DIR, f"user_{user_id}_device_{device_id}.json")
        
        if not os.path.exists(cache_file):
            return []
        
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        return [OfflineReport(**report) for report in cache.get("reports", [])]
    except Exception as e:
        print(f"Error loading offline reports: {e}")
        return []

def sync_offline_reports_to_database(reports: List[OfflineReport]) -> SyncResponse:
    """Sync offline reports to main database"""
    synced_count = 0
    failed_count = 0
    errors = []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for report in reports:
        try:
            # Insert into main reports table
            cursor.execute('''
                INSERT INTO reports (user_id, risk_type, latitude, longitude, location, description, timestamp, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.user_id, report.risk_type, report.latitude, report.longitude,
                report.location, report.description, report.timestamp, "synced"
            ))
            
            synced_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Failed to sync report {report.timestamp}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return SyncResponse(
        synced_reports=synced_count,
        failed_reports=failed_count,
        errors=errors
    )

def clear_offline_cache(user_id: int, device_id: str):
    """Clear offline cache after successful sync"""
    try:
        cache_file = os.path.join(OFFLINE_CACHE_DIR, f"user_{user_id}_device_{device_id}.json")
        if os.path.exists(cache_file):
            os.remove(cache_file)
    except Exception as e:
        print(f"Error clearing cache: {e}")

@router.post("/store-offline")
def store_offline_report(report: OfflineReport):
    """Store a report offline when no internet connection"""
    try:
        if save_offline_report(report):
            return {
                "status": "success",
                "message": "Report stored offline successfully",
                "report_id": f"offline_{report.timestamp}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store offline report")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offline storage failed: {str(e)}")

@router.get("/offline-reports/{user_id}/{device_id}")
def get_user_offline_reports(user_id: int, device_id: str):
    """Get all offline reports for a user"""
    try:
        reports = get_offline_reports(user_id, device_id)
        return {
            "status": "success",
            "reports": [report.dict() for report in reports],
            "count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get offline reports: {str(e)}")

@router.post("/sync")
def sync_offline_reports(sync_request: SyncRequest):
    """Sync offline reports to main database"""
    try:
        # Get offline reports
        offline_reports = get_offline_reports(sync_request.user_id, sync_request.device_id)
        
        if not offline_reports:
            return {
                "status": "success",
                "message": "No offline reports to sync",
                "synced_count": 0
            }
        
        # Sync to database
        sync_result = sync_offline_reports_to_database(offline_reports)
        
        # Clear cache if sync was successful
        if sync_result.failed_reports == 0:
            clear_offline_cache(sync_request.user_id, sync_request.device_id)
        
        return {
            "status": "success",
            "message": f"Synced {sync_result.synced_reports} reports",
            "synced_count": sync_result.synced_reports,
            "failed_count": sync_result.failed_reports,
            "errors": sync_result.errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/sync-status/{user_id}/{device_id}")
def get_sync_status(user_id: int, device_id: str):
    """Get sync status and pending reports count"""
    try:
        offline_reports = get_offline_reports(user_id, device_id)
        
        return {
            "status": "success",
            "pending_reports": len(offline_reports),
            "last_sync_attempt": None,  # Could be enhanced with actual sync history
            "needs_sync": len(offline_reports) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")

@router.delete("/clear-offline/{user_id}/{device_id}")
def clear_offline_data(user_id: int, device_id: str):
    """Clear all offline data for a user/device"""
    try:
        clear_offline_cache(user_id, device_id)
        return {
            "status": "success",
            "message": "Offline data cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear offline data: {str(e)}") 