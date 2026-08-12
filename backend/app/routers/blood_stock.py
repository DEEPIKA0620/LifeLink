from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.hospital import Hospital
from app.models.blood_stock import BloodStock
from app.schemas.auth import ApiResponse
from app.schemas.hospital import BloodStockUpdate

router = APIRouter(prefix="/api/blood-stock", tags=["Blood Stock"])

@router.get("", response_model=ApiResponse)
def get_all_blood_stock(blood_group: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(BloodStock)
    if blood_group:
        query = query.filter(BloodStock.blood_group == blood_group.upper())
    
    stock_items = query.all()
    results = []
    for s in stock_items:
        hospital = db.query(Hospital).filter(Hospital.id == s.hospital_id).first()
        results.append({
            "id": s.id,
            "hospital_id": s.hospital_id,
            "hospital_name": hospital.hospital_name if hospital else "Hospital Blood Bank",
            "city": hospital.city if hospital else "Bengaluru",
            "blood_group": s.blood_group,
            "units_available": s.units_available,
            "low_stock_threshold": s.low_stock_threshold,
            "status": "out_of_stock" if s.units_available == 0 else ("low_stock" if s.units_available <= s.low_stock_threshold else "in_stock"),
            "last_updated": s.last_updated.isoformat() if s.last_updated else None
        })
    return ApiResponse(success=True, message=f"Loaded {len(results)} blood stock records", data={"blood_stock": results})

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_or_add_blood_stock(
    blood_group: str,
    units_available: int,
    low_stock_threshold: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["hospital"]))
):
    if units_available < 0:
        raise HTTPException(status_code=400, detail="Blood units available cannot be negative")

    hospital = db.query(Hospital).filter(Hospital.user_id == current_user.id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital account profile not found")

    existing = db.query(BloodStock).filter(
        BloodStock.hospital_id == hospital.id,
        BloodStock.blood_group == blood_group.upper()
    ).first()

    if existing:
        existing.units_available = units_available
        existing.low_stock_threshold = low_stock_threshold
        db.commit()
        db.refresh(existing)
        target_item = existing
    else:
        target_item = BloodStock(
            hospital_id=hospital.id,
            blood_group=blood_group.upper(),
            units_available=units_available,
            low_stock_threshold=low_stock_threshold
        )
        db.add(target_item)
        db.commit()
        db.refresh(target_item)

    return ApiResponse(success=True, message="Blood stock updated successfully")

@router.put("/{id}", response_model=ApiResponse)
def update_blood_stock_by_id(
    id: int,
    req: BloodStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["hospital", "admin"]))
):
    if req.units_available < 0:
        raise HTTPException(status_code=400, detail="Blood units available cannot be negative")

    stock_item = db.query(BloodStock).filter(BloodStock.id == id).first()
    if not stock_item:
        raise HTTPException(status_code=404, detail="Blood stock record not found")

    stock_item.units_available = req.units_available
    if req.low_stock_threshold is not None:
        stock_item.low_stock_threshold = req.low_stock_threshold

    db.commit()
    return ApiResponse(success=True, message="Blood stock units updated")

@router.delete("/{id}", response_model=ApiResponse)
def delete_blood_stock_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["hospital", "admin"]))
):
    stock_item = db.query(BloodStock).filter(BloodStock.id == id).first()
    if not stock_item:
        raise HTTPException(status_code=404, detail="Blood stock record not found")
    
    db.delete(stock_item)
    db.commit()
    return ApiResponse(success=True, message="Blood stock record deleted")
