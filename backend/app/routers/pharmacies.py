from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.utils.distance import calculate_haversine_distance
from app.schemas.auth import ApiResponse
from app.schemas.pharmacy import PharmacyOut, PharmacyProfileUpdate

router = APIRouter(prefix="/api/pharmacies", tags=["Pharmacies"])

@router.get("", response_model=ApiResponse)
def list_pharmacies(city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Pharmacy).filter(Pharmacy.verified == True)
    if city:
        query = query.filter(Pharmacy.city.ilike(f"%{city}%"))
    pharmacies = query.all()
    results = [PharmacyOut.model_validate(p).model_dump() for p in pharmacies]
    return ApiResponse(success=True, message=f"Found {len(results)} pharmacies", data={"pharmacies": results})

@router.get("/nearby", response_model=ApiResponse)
def search_nearby_pharmacies(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(25.0),
    db: Session = Depends(get_db)
):
    pharmacies = db.query(Pharmacy).filter(Pharmacy.verified == True).all()
    nearby = []
    for p in pharmacies:
        dist = calculate_haversine_distance(lat, lon, p.latitude, p.longitude)
        if dist <= radius_km:
            data = PharmacyOut.model_validate(p).model_dump()
            data["distance_km"] = dist
            nearby.append(data)

    nearby.sort(key=lambda x: x["distance_km"])
    return ApiResponse(success=True, message=f"Found {len(nearby)} pharmacies within {radius_km} km", data={"pharmacies": nearby})

@router.get("/{id}", response_model=ApiResponse)
def get_pharmacy_detail(id: int, db: Session = Depends(get_db)):
    p = db.query(Pharmacy).filter(Pharmacy.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pharmacy record not found")
    return ApiResponse(success=True, message="Pharmacy detail", data=PharmacyOut.model_validate(p).model_dump())

@router.put("/profile", response_model=ApiResponse)
def update_pharmacy_profile(
    req: PharmacyProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["pharmacy"]))
):
    p = db.query(Pharmacy).filter(Pharmacy.user_id == current_user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pharmacy record not found")

    if req.pharmacy_name:
        p.pharmacy_name = req.pharmacy_name
    if req.phone:
        p.phone = req.phone
    if req.address:
        p.address = req.address
    if req.city:
        p.city = req.city
    if req.opening_time:
        p.opening_time = req.opening_time
    if req.closing_time:
        p.closing_time = req.closing_time
    if req.latitude:
        p.latitude = req.latitude
    if req.longitude:
        p.longitude = req.longitude

    db.commit()
    db.refresh(p)
    return ApiResponse(success=True, message="Pharmacy profile updated successfully")
