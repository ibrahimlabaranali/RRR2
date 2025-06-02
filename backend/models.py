from backend.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

# 🚚 USER MODEL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nin = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="driver", nullable=False)

    # Relationships
    reports = relationship("Report", back_populates="user", lazy="joined")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


# ⚠️ RISK REPORT MODEL
class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    risk_type = Column(String)
    description = Column(Text)
    location = Column(String)
    state = Column(String)
    lga = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reports")

    def __repr__(self):
        return f"<Report(id={self.id}, type={self.risk_type}, location={self.location})>"

    @staticmethod
    def get_all_reports(db):
        return db.query(Report).all()
