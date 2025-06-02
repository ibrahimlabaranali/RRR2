# Pydantic schemas

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ----------------------
# 🔐 USER SCHEMAS
# ----------------------

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nin: str = Field(..., min_length=11, max_length=11, description="Nigerian Identification Number (11 digits)")
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    role: Optional[str] = Field(default="driver", description="Role: driver, admin, viewer")

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    nin: str
    role: str

    class Config:
        orm_mode = True


# ----------------------
# 📍 REPORT SCHEMAS
# ----------------------

class ReportCreate(BaseModel):
    user_id: int
    risk_type: str = Field(..., description="Type of risk: Banditry, Robbery, Flooding, etc.")
    description: Optional[str] = Field(None, description="Additional details about the incident")
    location: Optional[str] = Field(None, description="Free-text location (e.g. 'Kaduna-Abuja Road')")
    state: str = Field(..., description="Nigerian state (e.g. Kaduna)")
    lga: str = Field(..., description="Local Government Area (e.g. Chikun)")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")

class ReportResponse(BaseModel):
    id: int
    user_id: int
    risk_type: str
    description: Optional[str]
    location: Optional[str]
    state: str
    lga: str
    lat: float
    lon: float
    timestamp: datetime

    class Config:
        orm_mode = True


# ----------------------
# 🤖 AI CLASSIFIER SCHEMAS
# ----------------------

class RiskTextInput(BaseModel):
    text: str = Field(..., description="Description of the incident to classify")

class RiskPrediction(BaseModel):
    predicted_label: str
    confidence: float
