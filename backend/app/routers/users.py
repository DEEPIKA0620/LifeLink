from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.schemas.auth import ApiResponse

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=ApiResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        message="User profile retrieved",
        data=UserOut.model_validate(current_user).model_dump()
    )

@router.put("/me", response_model=ApiResponse)
def update_user_profile(req: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.phone is not None:
        current_user.phone = req.phone
    if req.address is not None:
        current_user.address = req.address
    if req.city is not None:
        current_user.city = req.city
    if req.latitude is not None:
        current_user.latitude = req.latitude
    if req.longitude is not None:
        current_user.longitude = req.longitude

    db.commit()
    db.refresh(current_user)

    return ApiResponse(
        success=True,
        message="Profile updated successfully",
        data=UserOut.model_validate(current_user).model_dump()
    )
