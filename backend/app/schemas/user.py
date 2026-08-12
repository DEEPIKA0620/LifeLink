from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str
    address: str
    city: str
    latitude: float
    longitude: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
