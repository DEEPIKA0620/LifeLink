from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.utils.distance import calculate_haversine_distance, estimate_travel_time_minutes, format_travel_time_label
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
            "dosage_form": getattr(m, "dosage_form", None) or "Tablet",
            "strength": getattr(m, "strength", None) or "",
            "quantity": m.quantity,
            "unit": m.unit,
            "price": float(m.price),
            "availability_status": m.availability_status,
            "last_updated": m.last_updated.isoformat() if m.last_updated else None
        })
    return ApiResponse(success=True, message=f"Loaded {len(results)} medicines", data={"medicines": results})

@router.get("/search", response_model=ApiResponse)
def search_medicines(
    q: Optional[str] = Query(None, description="Medicine name, generic name, or strength query"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    availability: Optional[str] = None,
    dosage_form: Optional[str] = None,
    strength: Optional[str] = None,
    lat: Optional[float] = Query(None, description="Search origin latitude for distance calculation"),
    lon: Optional[float] = Query(None, description="Search origin longitude for distance calculation"),
    radius_km: Optional[float] = Query(None, description="Maximum search radius in km"),
    sort: Optional[str] = Query("default", description="'nearest', 'price_asc', 'price_desc', or 'default'"),
    db: Session = Depends(get_db)
):
    """
    Full-featured medicine search supporting name, generic name, category, strength,
    city, availability status, and geospatial radius-based distance calculation.
    """
    query = db.query(Medicine).join(Pharmacy, Medicine.pharmacy_id == Pharmacy.id)

    if q and q.strip():
        term = q.strip()
        query = query.filter(
            (Medicine.medicine_name.ilike(f"%{term}%")) |
            (Medicine.generic_name.ilike(f"%{term}%")) |
            (Medicine.category.ilike(f"%{term}%"))
        )

    if category and category.lower() != "all":
        query = query.filter(Medicine.category.ilike(f"%{category}%"))

    if availability and availability.lower() not in ["all", "any"]:
        query = query.filter(Medicine.availability_status == availability.lower())

    if city and city.lower() != "all":
        query = query.filter(Pharmacy.city.ilike(f"%{city}%"))

    if dosage_form and dosage_form.lower() != "all":
        query = query.filter(Medicine.dosage_form.ilike(f"%{dosage_form}%"))

    if strength:
        query = query.filter(Medicine.strength.ilike(f"%{strength}%"))

    matches = query.all()
    results = []

    for m in matches:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == m.pharmacy_id).first()
        dist = None
        est_mins = None
        travel_label = None

        if lat is not None and lon is not None and pharmacy and pharmacy.latitude and pharmacy.longitude:
            dist = calculate_haversine_distance(lat, lon, pharmacy.latitude, pharmacy.longitude)
            if radius_km is not None and dist > radius_km:
                continue
            est_mins = estimate_travel_time_minutes(dist)
            travel_label = format_travel_time_label(est_mins)

        results.append({
            "id": m.id,
            "pharmacy_id": m.pharmacy_id,
            "pharmacy_name": pharmacy.pharmacy_name if pharmacy else "Pharmacy",
            "phone": pharmacy.phone if pharmacy else "+91 9900000000",
            "address": pharmacy.address if pharmacy else "Branch Address",
            "city": pharmacy.city if pharmacy else "Bengaluru",
            "opening_time": pharmacy.opening_time if pharmacy else "08:00",
            "closing_time": pharmacy.closing_time if pharmacy else "22:00",
            "medicine_name": m.medicine_name,
            "generic_name": m.generic_name,
            "category": m.category,
            "dosage_form": getattr(m, "dosage_form", None) or "Tablet",
            "strength": getattr(m, "strength", None) or "",
            "quantity": m.quantity,
            "unit": m.unit,
            "price": float(m.price),
            "availability_status": m.availability_status,
            "distance_km": dist,
            "estimated_minutes": est_mins,
            "travel_time_label": travel_label,
            "latitude": pharmacy.latitude if pharmacy else 12.9716,
            "longitude": pharmacy.longitude if pharmacy else 77.5946,
            "last_updated": m.last_updated.isoformat() if m.last_updated else None
        })

    # Sort results
    if sort == "price_asc":
        results.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        results.sort(key=lambda x: -x["price"])
    elif sort == "nearest" and lat is not None and lon is not None:
        results.sort(key=lambda x: (x["distance_km"] if x["distance_km"] is not None else 9999))
    elif lat is not None and lon is not None:
        results.sort(key=lambda x: (x["distance_km"] if x["distance_km"] is not None else 9999))

    return ApiResponse(
        success=True,
        message=f"Found {len(results)} medicines matching query",
        data={"medicines": results, "total_found": len(results)}
    )

@router.get("/nearby", response_model=ApiResponse)
def search_nearby_medicines(
    q: Optional[str] = Query(None, description="Medicine query"),
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(25.0),
    db: Session = Depends(get_db)
):
    return search_medicines(q=q, lat=lat, lon=lon, radius_km=radius_km, db=db)

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
