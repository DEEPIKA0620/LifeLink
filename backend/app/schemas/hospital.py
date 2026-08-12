from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserOut

class BloodStockOut(BaseModel):
    id: int
    hospital_id: int
    blood_group: str
    units_available: int
    low_stock_threshold: int
    last_updated: datetime

    class Config:
        from_attributes = True

class BloodStockUpdate(BaseModel):
    units_available: int
    low_stock_threshold: Optional[int] = 5

class HospitalOut(BaseModel):
    id: int
    user_id: int
    hospital_name: str
    registration_number: str
    phone: str
    address: str
    city: str
    latitude: float
    longitude: float
    verified: bool
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class HospitalProfileUpdate(BaseModel):
    hospital_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
