from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_name = Column(String(150), nullable=False)
    registration_number = Column(String(80), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="hospital_profile")
    blood_stock = relationship("BloodStock", back_populates="hospital", cascade="all, delete-orphan")
    requests = relationship("BloodRequest", back_populates="hospital")
    donations = relationship("DonationHistory", back_populates="hospital")
