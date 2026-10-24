from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    full_name: str

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6)
    confirm_password: Optional[str] = None
    role: str = Field(..., description="patient, donor, hospital, pharmacy")
    address: Optional[str] = ""
    city: Optional[str] = "Bangalore"
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0

    # Donor Specific Fields
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    last_donation_date: Optional[date] = None
    availability_status: Optional[str] = "available"

    # Hospital Specific Fields
    hospital_name: Optional[str] = None
    registration_number: Optional[str] = None

    # Pharmacy Specific Fields
    pharmacy_name: Optional[str] = None
    opening_time: Optional[str] = "08:00"
    closing_time: Optional[str] = "22:00"

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
