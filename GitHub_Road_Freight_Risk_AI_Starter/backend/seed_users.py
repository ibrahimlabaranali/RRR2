from backend.database import SessionLocal
from backend.models import User
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(username, nin, password, role):
    hashed_pw = pwd_context.hash(password)
    user = User(username=username, nin=nin, password=hashed_pw, role=role)
    db.add(user)

users = [
    ("admin", "23456789011", "admin123", "admin"),
    ("driver1", "23456789012", "driver123", "driver"),
    ("viewer1", "23456789013", "viewer123", "viewer")
]

for u in users:
    create_user(*u)

db.commit()
print("✅ Seeded users.")
