from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    pharmacy_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    opening_time = Column(String(10), default="08:00")
    closing_time = Column(String(10), default="22:00")
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="pharmacy_profile")
    medicines = relationship("Medicine", back_populates="pharmacy", cascade="all, delete-orphan")
