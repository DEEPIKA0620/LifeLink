from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    blood_group = Column(String(10), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    last_donation_date = Column(Date, nullable=True)
    availability_status = Column(String(20), default="available", index=True) # available, unavailable
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    city = Column(String(100), nullable=False, index=True)
    response_rate = Column(Float, default=100.0)
    total_donations = Column(Integer, default=0)
    verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="donor_profile")
    matches = relationship("DonorMatch", back_populates="donor", cascade="all, delete-orphan")
    donation_history = relationship("DonationHistory", back_populates="donor", cascade="all, delete-orphan")
