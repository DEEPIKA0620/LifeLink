from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserOut

class BloodRequestCreate(BaseModel):
    blood_group: str
    units_required: int = 1
    priority: str = "normal" # critical, urgent, normal
    required_by: datetime
    hospital_name: str
    hospital_id: Optional[int] = None
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    additional_notes: Optional[str] = None

class DonorMatchOut(BaseModel):
    id: int
    request_id: int
    donor_id: int
    match_score: int
    distance_km: float
    estimated_minutes: int
    blood_compatibility: int
    availability_score: int
    distance_score: int
    response_score: int
    eligibility_score: int
    match_reasons: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class BloodRequestOut(BaseModel):
    id: int
    requester_id: int
    hospital_id: Optional[int] = None
    blood_group: str
    units_required: int
    priority: str
    required_by: datetime
    latitude: float
    longitude: float
    hospital_name: str
    additional_notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    requester: Optional[UserOut] = None

    class Config:
        from_attributes = True
