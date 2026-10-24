from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DonationHistory(Base):
    __tablename__ = "donation_history"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("donors.id", ondelete="CASCADE"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id", ondelete="SET NULL"), nullable=True)
    donation_date = Column(Date, nullable=False)
    blood_group = Column(String(10), nullable=False)
    units = Column(Integer, default=1)
    status = Column(String(20), default="completed", index=True) # completed, scheduled, cancelled
    donation_type = Column(String(50), default="Whole Blood") # Whole Blood, Platelets, Plasma, Red Blood Cells
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    donor = relationship("Donor", back_populates="donation_history")
    hospital = relationship("Hospital", back_populates="donations")
    blood_request = relationship("BloodRequest", foreign_keys=[request_id])
