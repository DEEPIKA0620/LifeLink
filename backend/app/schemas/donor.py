from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.schemas.user import UserOut

class DonorOut(BaseModel):
    id: int
    user_id: int
    blood_group: str
    date_of_birth: date
    last_donation_date: Optional[date] = None
    availability_status: str
    latitude: float
    longitude: float
    city: str
    response_rate: float
    total_donations: int
    verified: bool
    created_at: datetime
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True

class DonorProfileUpdate(BaseModel):
    blood_group: Optional[str] = None
    last_donation_date: Optional[date] = None
    availability_status: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AvailabilityUpdate(BaseModel):
    availability_status: str # available, unavailable
