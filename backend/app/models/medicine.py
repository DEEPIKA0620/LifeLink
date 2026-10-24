from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False)
    medicine_name = Column(String(150), nullable=False, index=True)
    generic_name = Column(String(150), nullable=False, index=True)
    category = Column(String(100), default="General", index=True)
    dosage_form = Column(String(50), nullable=True) # Tablet, Capsule, Syrup, Inhaler, Drops, Ointment
    strength = Column(String(50), nullable=True) # 650mg, 500mg, 10mg, etc.
    quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String(50), default="strips")
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    availability_status = Column(String(20), default="in_stock", index=True) # in_stock, low_stock, out_of_stock
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="medicines")
