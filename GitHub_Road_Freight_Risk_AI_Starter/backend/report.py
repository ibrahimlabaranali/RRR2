# Report API
from fastapi import Security, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import get_db  # Make sure this import path matches your project structure
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

# Define your secret key and algorithm here
SECRET_KEY = "your_secret_key_here"  # Replace with your actual secret key
ALGORITHM = "HS256"  # Or the algorithm you use for JWT

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Security(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=403, detail="Not authorized")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload.get("sub"), "role": payload.get("role")}
    except JWTError:
        raise credentials_exception
from .schemas import RiskReportOut  # Make sure this import path matches your project structure
from .models import RiskReport  # Make sure this import path matches your project structure

@router.get("/reports", response_model=list[RiskReportOut])
def get_reports(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all reports")
    return db.query(RiskReport).all()
