from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.utils.distance import calculate_haversine_distance
from app.schemas.auth import ApiResponse
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineOut

router = APIRouter(prefix="/api/medicines", tags=["Medicines"])

@router.get("", response_model=ApiResponse)
def list_medicines(pharmacy_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Medicine)
    if pharmacy_id:
        query = query.filter(Medicine.pharmacy_id == pharmacy_id)
    medicines = query.all()
    results = []
    for m in medicines:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == m.pharmacy_id).first()
        results.append({
            "id": m.id,
            "pharmacy_id": m.pharmacy_id,
            "pharmacy_name": pharmacy.pharmacy_name if pharmacy else "Pharmacy",
            "city": pharmacy.city if pharmacy else "Bengaluru",
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name,
            "category": m.category,
            "quantity": m.quantity,
            "unit": m.unit,
            "price": float(m.price),
            "availability_status": m.availability_status,
            "last_updated": m.last_updated.isoformat() if m.last_updated else None
        })
    return ApiResponse(success=True, message=f"Loaded {len(results)} medicines", data={"medicines": results})

@router.get("/search", response_model=ApiResponse)
def search_medicines(
    q: str = Query(..., description="Medicine or generic name query"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    availability: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Medicine).join(Pharmacy)
    if q:
        query = query.filter(
            (Medicine.medicine_name.ilike(f"%{q}%")) |
            (Medicine.generic_name.ilike(f"%{q}%"))
        )
    if category:
        query = query.filter(Medicine.category.ilike(f"%{category}%"))
    if availability:
        query = query.filter(Medicine.availability_status == availability)
    if city:
        query = query.filter(Pharmacy.city.ilike(f"%{city}%"))

    matches = query.all()
    results = []
    for m in matches:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == m.pharmacy_id).first()
        results.append({
            "id": m.id,
            "pharmacy_id": m.pharmacy_id,
            "pharmacy_name": pharmacy.pharmacy_name if pharmacy else "Pharmacy",
            "phone": pharmacy.phone if pharmacy else "",
            "address": pharmacy.address if pharmacy else "",
            "city": pharmacy.city if pharmacy else "Bengaluru",
            "opening_time": pharmacy.opening_time if pharmacy else "08:00",
            "closing_time": pharmacy.closing_time if pharmacy else "22:00",
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name,
            "category": m.category,
            "quantity": m.quantity,
            "unit": m.unit,
            "price": float(m.price),
            "availability_status": m.availability_status,
            "latitude": pharmacy.latitude if pharmacy else 12.9716,
            "longitude": pharmacy.longitude if pharmacy else 77.5946
        })

    return ApiResponse(success=True, message=f"Found {len(results)} medicines matching query", data={"medicines": results})

@router.get("/nearby", response_model=ApiResponse)
def search_nearby_medicines(
    q: str = Query(..., description="Medicine query"),
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(25.0),
    db: Session = Depends(get_db)
):
    query = db.query(Medicine).filter(
        (Medicine.medicine_name.ilike(f"%{q}%")) |
        (Medicine.generic_name.ilike(f"%{q}%"))
    )
    medicines = query.all()
    nearby = []
    for m in medicines:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == m.pharmacy_id).first()
        if pharmacy:
            dist = calculate_haversine_distance(lat, lon, pharmacy.latitude, pharmacy.longitude)
            if dist <= radius_km:
                nearby.append({
                    "id": m.id,
                    "pharmacy_id": m.pharmacy_id,
                    "pharmacy_name": pharmacy.pharmacy_name,
                    "phone": pharmacy.phone,
                    "address": pharmacy.address,
                    "city": pharmacy.city,
                    "medicine_name": m.medicine_name,
                    "generic_name": m.generic_name,
                    "category": m.category,
                    "quantity": m.quantity,
                    "unit": m.unit,
                    "price": float(m.price),
                    "availability_status": m.availability_status,
                    "distance_km": dist,
                    "latitude": pharmacy.latitude,
                    "longitude": pharmacy.longitude
                })

    nearby.sort(key=lambda x: x["distance_km"])
    return ApiResponse(success=True, message=f"Found {len(nearby)} nearby medicine matches within {radius_km} km", data={"medicines": nearby})

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    req: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["pharmacy"]))
):
    pharmacy = db.query(Pharmacy).filter(Pharmacy.user_id == current_user.id).first()
    if not pharmacy:
        raise HTTPException(status_code=404, detail="Pharmacy profile not found")

    status_str = req.availability_status
    if req.quantity == 0:
        status_str = "out_of_stock"
    elif req.quantity <= 5:
        status_str = "low_stock"

    med = Medicine(
        pharmacy_id=pharmacy.id,
        medicine_name=req.medicine_name,
        generic_name=req.generic_name,
        category=req.category or "General",
        quantity=req.quantity,
        unit=req.unit or "strips",
        price=req.price,
        availability_status=status_str
    )
    db.add(med)
    db.commit()
    db.refresh(med)

    return ApiResponse(success=True, message="Medicine added successfully", data=MedicineOut.model_validate(med).model_dump())

@router.put("/{id}", response_model=ApiResponse)
def update_medicine(
    id: int,
    req: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["pharmacy", "admin"]))
):
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine record not found")

    if req.medicine_name is not None:
        med.medicine_name = req.medicine_name
    if req.generic_name is not None:
        med.generic_name = req.generic_name
    if req.category is not None:
        med.category = req.category
    if req.quantity is not None:
        med.quantity = req.quantity
        if med.quantity == 0:
            med.availability_status = "out_of_stock"
        elif med.quantity <= 5:
            med.availability_status = "low_stock"
        else:
            med.availability_status = "in_stock"
    if req.unit is not None:
        med.unit = req.unit
    if req.price is not None:
        med.price = req.price
    if req.availability_status is not None:
        med.availability_status = req.availability_status

    db.commit()
    db.refresh(med)
    return ApiResponse(success=True, message="Medicine record updated successfully")

@router.delete("/{id}", response_model=ApiResponse)
def delete_medicine(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["pharmacy", "admin"]))
):
    med = db.query(Medicine).filter(Medicine.id == id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    db.delete(med)
    db.commit()
    return ApiResponse(success=True, message="Medicine record deleted successfully")
