from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.hospital import Hospital
from app.models.blood_stock import BloodStock
from app.utils.distance import calculate_haversine_distance
from app.schemas.auth import ApiResponse
from app.schemas.hospital import HospitalOut, HospitalProfileUpdate, BloodStockUpdate

router = APIRouter(prefix="/api/hospitals", tags=["Hospitals"])

@router.get("", response_model=ApiResponse)
def list_hospitals(city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Hospital).filter(Hospital.verified == True)
    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))
    hospitals = query.all()
    results = [HospitalOut.model_validate(h).model_dump() for h in hospitals]
    return ApiResponse(success=True, message=f"Found {len(results)} hospitals", data={"hospitals": results})

@router.get("/nearby", response_model=ApiResponse)
def search_nearby_hospitals(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(25.0),
    db: Session = Depends(get_db)
):
    hospitals = db.query(Hospital).filter(Hospital.verified == True).all()
    nearby = []
    for h in hospitals:
        dist = calculate_haversine_distance(lat, lon, h.latitude, h.longitude)
        if dist <= radius_km:
            data = HospitalOut.model_validate(h).model_dump()
            data["distance_km"] = dist
            nearby.append(data)

    nearby.sort(key=lambda x: x["distance_km"])
    return ApiResponse(success=True, message=f"Found {len(nearby)} hospitals within {radius_km} km", data={"hospitals": nearby})

@router.get("/{id}", response_model=ApiResponse)
def get_hospital_detail(id: int, db: Session = Depends(get_db)):
    h = db.query(Hospital).filter(Hospital.id == id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return ApiResponse(success=True, message="Hospital detail", data=HospitalOut.model_validate(h).model_dump())

@router.put("/profile", response_model=ApiResponse)
def update_hospital_profile(
    req: HospitalProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["hospital"]))
):
    h = db.query(Hospital).filter(Hospital.user_id == current_user.id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital record not found")

    if req.hospital_name:
        h.hospital_name = req.hospital_name
    if req.phone:
        h.phone = req.phone
    if req.address:
        h.address = req.address
    if req.city:
        h.city = req.city
    if req.latitude:
        h.latitude = req.latitude
    if req.longitude:
        h.longitude = req.longitude

    db.commit()
    db.refresh(h)
    return ApiResponse(success=True, message="Hospital profile updated successfully")

@router.get("/{hospital_id}/blood-stock", response_model=ApiResponse)
def get_hospital_blood_stock(hospital_id: int, db: Session = Depends(get_db)):
    stock = db.query(BloodStock).filter(BloodStock.hospital_id == hospital_id).all()
    results = [{
        "id": s.id,
        "hospital_id": s.hospital_id,
        "blood_group": s.blood_group,
        "units_available": s.units_available,
        "low_stock_threshold": s.low_stock_threshold,
        "status": "out_of_stock" if s.units_available == 0 else ("low_stock" if s.units_available <= s.low_stock_threshold else "in_stock"),
        "last_updated": s.last_updated.isoformat()
    } for s in stock]
    return ApiResponse(success=True, message="Blood stock loaded", data={"blood_stock": results})
