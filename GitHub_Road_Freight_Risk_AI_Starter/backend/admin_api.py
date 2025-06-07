# admin_api.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# Allow frontend (Streamlit) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "reports.db"

class RiskReport(BaseModel):
    username: str
    location: str
    lat: float
    lon: float
    state: str
    lga: str
    risk_type: str
    description: str
    timestamp: str

@app.post("/reports/")
def submit_report(report: RiskReport):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            location TEXT,
            lat REAL,
            lon REAL,
            state TEXT,
            lga TEXT,
            risk_type TEXT,
            description TEXT,
            timestamp TEXT
        )''')
        c.execute('''INSERT INTO reports (username, location, lat, lon, state, lga, risk_type, description, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (report.username, report.location, report.lat, report.lon, report.state,
                   report.lga, report.risk_type, report.description, report.timestamp))
        conn.commit()
        conn.close()
        return {"message": "Report submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/")
def get_all_reports():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM reports", conn)
    conn.close()
    return df.to_dict(orient="records")
