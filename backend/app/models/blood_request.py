from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    blood_group = Column(String(10), nullable=False, index=True)
    units_required = Column(Integer, nullable=False, default=1)
    priority = Column(String(20), default="normal", index=True) # critical, urgent, normal
    required_by = Column(DateTime, nullable=False)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    hospital_name = Column(String(150), nullable=False)
    additional_notes = Column(Text, nullable=True)
    status = Column(String(30), default="pending", index=True) # pending, searching, donor_notified, donor_accepted, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requester = relationship("User", back_populates="blood_requests")
    hospital = relationship("Hospital", back_populates="requests")
    matches = relationship("DonorMatch", back_populates="request", cascade="all, delete-orphan")
    status_history = relationship("RequestStatusHistory", back_populates="request", cascade="all, delete-orphan")
