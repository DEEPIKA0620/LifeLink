from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="patient") # patient, donor, hospital, pharmacy, admin
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    donor_profile = relationship("Donor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    hospital_profile = relationship("Hospital", back_populates="user", uselist=False, cascade="all, delete-orphan")
    pharmacy_profile = relationship("Pharmacy", back_populates="user", uselist=False, cascade="all, delete-orphan")
    blood_requests = relationship("BloodRequest", back_populates="requester", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
