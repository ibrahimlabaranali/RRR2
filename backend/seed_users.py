from backend.database import SessionLocal
from backend.models import User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a single DB session
db = SessionLocal()

def create_user(username, nin, password, role):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"⚠️ User '{username}' already exists. Skipping.")
        return

    hashed_pw = pwd_context.hash(password)
    user = User(username=username, nin=nin, password=hashed_pw, role=role)
    db.add(user)
    print(f"✅ Created user: {username} ({role})")

# List of users to seed
users = [
    ("admin", "23456789011", "admin123", "admin"),
    ("driver1", "23456789012", "driver123", "driver"),
    ("viewer1", "23456789013", "viewer123", "viewer")
]

try:
    for u in users:
        create_user(*u)
    db.commit()
    print("🎉 Finished seeding users.")
except IntegrityError as e:
    db.rollback()
    print("❌ Error during seeding:", e)
finally:
    db.close()
