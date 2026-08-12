from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DonorMatch(Base):
    __tablename__ = "donor_matches"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Integer, nullable=False, default=0)
    distance_km = Column(Float, default=0.0)
    estimated_minutes = Column(Integer, default=0)
    blood_compatibility = Column(Integer, default=0)
    availability_score = Column(Integer, default=0)
    distance_score = Column(Integer, default=0)
    response_score = Column(Integer, default=0)
    eligibility_score = Column(Integer, default=0)
    match_reasons = Column(Text, nullable=True)
    status = Column(String(20), default="notified", index=True) # notified, accepted, rejected, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request = relationship("BloodRequest", back_populates="matches")
    donor = relationship("Donor", back_populates="matches")
