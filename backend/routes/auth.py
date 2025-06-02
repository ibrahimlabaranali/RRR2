from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import sha256_crypt
from backend.models import User
from backend.schemas import UserCreate, UserLogin, UserResponse
from backend.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Dummy NIN format verification
def mock_nin_verification(nin: str) -> bool:
    return nin.startswith("2") and len(nin) == 11

# 🔐 Register endpoint
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not mock_nin_verification(user.nin):
        raise HTTPException(status_code=400, detail="Invalid NIN format")

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed_pw = sha256_crypt.hash(user.password)
    new_user = User(
        username=user.username,
        nin=user.nin,
        password=hashed_pw,
        role="driver"  # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 🔐 Login endpoint
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not sha256_crypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "username": db_user.username,
        "role": db_user.role
    }

# 🔐 Admin-only: List all users
@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Example for a Pydantic model in backend/schemas.py
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    username: str
    nin: str
    role: str

    class Config:
        from_attributes = True  # For Pydantic v2 ORM mode
