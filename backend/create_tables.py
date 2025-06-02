from backend.database import Base, engine
from backend import models  # ✅ import models directly

# ✅ Create tables using the SQLAlchemy Base metadata
Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully.")
