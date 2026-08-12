from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOut

class PharmacyOut(BaseModel):
    id: int
    user_id: int
    pharmacy_name: str
    phone: str
    address: str
    city: str
    latitude: float
    longitude: float
    opening_time: str
    closing_time: str
    verified: bool
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class PharmacyProfileUpdate(BaseModel):
    pharmacy_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
