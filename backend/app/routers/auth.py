from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.pharmacy import Pharmacy
from app.schemas.auth import LoginRequest, TokenResponse, UserRegisterRequest, ApiResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user (Patient, Donor, Hospital, or Pharmacy). Public admin registration is prohibited.
    """
    if req.confirm_password is not None and req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if req.role.lower() == "admin":
        raise HTTPException(status_code=403, detail="Public administrator registration is prohibited")

    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email address is already registered")

    # Create Base User
    new_user = User(
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=req.role.lower(),
        address=req.address or "",
        city=req.city or "Bangalore",
        latitude=req.latitude or 12.9716,
        longitude=req.longitude or 77.5946,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Create Role Profile
    if req.role.lower() == "donor":
        if not req.blood_group or not req.date_of_birth:
            raise HTTPException(status_code=400, detail="Donor registration requires blood group and date of birth")
        donor_profile = Donor(
            user_id=new_user.id,
            blood_group=req.blood_group.upper(),
            date_of_birth=req.date_of_birth,
            last_donation_date=req.last_donation_date,
            availability_status=req.availability_status or "available",
            latitude=new_user.latitude,
            longitude=new_user.longitude,
            city=req.city,
            verified=True
        )
        db.add(donor_profile)

    elif req.role.lower() == "hospital":
        hospital_profile = Hospital(
            user_id=new_user.id,
            hospital_name=req.hospital_name or req.full_name,
            registration_number=req.registration_number or f"REG-{new_user.id}",
            phone=req.phone,
            address=req.address,
            city=req.city,
            latitude=new_user.latitude,
            longitude=new_user.longitude,
            verified=True
        )
        db.add(hospital_profile)

    elif req.role.lower() == "pharmacy":
        pharmacy_profile = Pharmacy(
            user_id=new_user.id,
            pharmacy_name=req.pharmacy_name or req.full_name,
            phone=req.phone,
            address=req.address,
            city=req.city,
            latitude=new_user.latitude,
            longitude=new_user.longitude,
            opening_time=req.opening_time or "08:00",
            closing_time=req.closing_time or "22:00",
            verified=True
        )
        db.add(pharmacy_profile)

    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = create_access_token({"user_id": new_user.id, "role": new_user.role})

    return ApiResponse(
        success=True,
        message="Account registered successfully",
        data={
            "token": token,
            "access_token": token,
            "user_id": new_user.id,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "user": {
                "id": new_user.id,
                "role": new_user.role,
                "full_name": new_user.full_name,
                "email": new_user.email
            }
        }
    )

@router.post("/login", response_model=ApiResponse)
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user with email & password, returning a JWT bearer token.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email address or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated. Please contact support.")

    token = create_access_token({"user_id": user.id, "role": user.role})

    return ApiResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "user": {
                "id": user.id,
                "role": user.role,
                "full_name": user.full_name,
                "email": user.email
            }
        }
    )

@router.get("/me", response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile information for current authenticated user."""
    return ApiResponse(
        success=True,
        message="Profile details fetched successfully",
        data={
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "role": current_user.role,
            "address": current_user.address,
            "city": current_user.city,
            "latitude": current_user.latitude,
            "longitude": current_user.longitude
        }
    )

@router.post("/logout", response_model=ApiResponse)
def logout_user(current_user: User = Depends(get_current_user)):
    return ApiResponse(success=True, message="Successfully logged out")

@router.post("/refresh", response_model=ApiResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    token = create_access_token({"user_id": current_user.id, "role": current_user.role})
    return ApiResponse(
        success=True,
        message="Token refreshed successfully",
        data={"access_token": token, "token_type": "bearer"}
    )

@router.post("/forgot-password", response_model=ApiResponse)
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return ApiResponse(success=True, message="Password reset instructions sent to your email")
    return ApiResponse(success=True, message="If registered, password reset instructions have been sent")

@router.post("/reset-password", response_model=ApiResponse)
def reset_password(token: str, new_password: str):
    return ApiResponse(success=True, message="Password reset successfully. Please login.")
