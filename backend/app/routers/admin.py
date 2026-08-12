from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine
from app.models.blood_request import BloodRequest
from app.models.donor_match import DonorMatch
from app.models.audit_log import AuditLog
from app.schemas.auth import ApiResponse

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])

# Require Admin Role for all endpoints in this router
admin_only = Depends(RoleChecker(["admin"]))

@router.get("/dashboard", response_model=ApiResponse, dependencies=[admin_only])
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns platform key performance metrics and distribution charts data.
    """
    total_users = db.query(User).count()
    total_donors = db.query(Donor).count()
    available_donors = db.query(Donor).filter(Donor.availability_status == "available").count()
    total_hospitals = db.query(Hospital).count()
    total_pharmacies = db.query(Pharmacy).count()
    active_requests = db.query(BloodRequest).filter(BloodRequest.status.in_(["pending", "searching", "donor_notified", "donor_accepted"])).count()
    completed_requests = db.query(BloodRequest).filter(BloodRequest.status == "completed").count()
    total_medicines = db.query(Medicine).count()

    # 1. Blood Group Distribution Chart Data
    bg_distribution = db.query(
        Donor.blood_group, func.count(Donor.id)
    ).group_by(Donor.blood_group).all()
    bg_chart = {bg: count for bg, count in bg_distribution}

    # 2. Requests by Priority Chart Data
    priority_distribution = db.query(
        BloodRequest.priority, func.count(BloodRequest.id)
    ).group_by(BloodRequest.priority).all()
    priority_chart = {p: count for p, count in priority_distribution}

    # 3. Requests by Status Chart Data
    status_distribution = db.query(
        BloodRequest.status, func.count(BloodRequest.id)
    ).group_by(BloodRequest.status).all()
    status_chart = {s: count for s, count in status_distribution}

    return ApiResponse(
        success=True,
        message="Admin statistics loaded successfully",
        data={
            "stats": {
                "total_users": total_users,
                "total_donors": total_donors,
                "available_donors": available_donors,
                "total_hospitals": total_hospitals,
                "total_pharmacies": total_pharmacies,
                "active_requests": active_requests,
                "completed_requests": completed_requests,
                "total_medicines": total_medicines
            },
            "charts": {
                "blood_group_distribution": bg_chart,
                "requests_by_priority": priority_chart,
                "requests_by_status": status_chart
            }
        }
    )

@router.get("/users", response_model=ApiResponse, dependencies=[admin_only])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "city": u.city,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat()
    } for u in users]
    return ApiResponse(success=True, message=f"Loaded {len(results)} users", data={"users": results})

@router.get("/donors", response_model=ApiResponse, dependencies=[admin_only])
def get_all_donors_admin(db: Session = Depends(get_db)):
    donors = db.query(Donor).all()
    results = [{
        "id": d.id,
        "full_name": d.user.full_name if d.user else "Donor",
        "email": d.user.email if d.user else "",
        "phone": d.user.phone if d.user else "",
        "blood_group": d.blood_group,
        "city": d.city,
        "availability_status": d.availability_status,
        "response_rate": d.response_rate,
        "total_donations": d.total_donations,
        "verified": d.verified
    } for d in donors]
    return ApiResponse(success=True, message=f"Loaded {len(results)} donors", data={"donors": results})

@router.get("/hospitals", response_model=ApiResponse, dependencies=[admin_only])
def get_all_hospitals_admin(db: Session = Depends(get_db)):
    hospitals = db.query(Hospital).all()
    results = [{
        "id": h.id,
        "hospital_name": h.hospital_name,
        "registration_number": h.registration_number,
        "phone": h.phone,
        "city": h.city,
        "verified": h.verified
    } for h in hospitals]
    return ApiResponse(success=True, message=f"Loaded {len(results)} hospitals", data={"hospitals": results})

@router.get("/pharmacies", response_model=ApiResponse, dependencies=[admin_only])
def get_all_pharmacies_admin(db: Session = Depends(get_db)):
    pharmacies = db.query(Pharmacy).all()
    results = [{
        "id": p.id,
        "pharmacy_name": p.pharmacy_name,
        "phone": p.phone,
        "city": p.city,
        "opening_time": p.opening_time,
        "closing_time": p.closing_time,
        "verified": p.verified
    } for p in pharmacies]
    return ApiResponse(success=True, message=f"Loaded {len(results)} pharmacies", data={"pharmacies": results})

@router.get("/requests", response_model=ApiResponse, dependencies=[admin_only])
def get_all_requests_admin(db: Session = Depends(get_db)):
    requests = db.query(BloodRequest).order_by(BloodRequest.created_at.desc()).all()
    results = [{
        "id": r.id,
        "requester_name": r.requester.full_name if r.requester else "Patient",
        "hospital_name": r.hospital_name,
        "blood_group": r.blood_group,
        "units_required": r.units_required,
        "priority": r.priority,
        "status": r.status,
        "created_at": r.created_at.isoformat()
    } for r in requests]
    return ApiResponse(success=True, message=f"Loaded {len(results)} requests", data={"requests": results})

@router.get("/reports", response_model=ApiResponse, dependencies=[admin_only])
def get_reports_admin(db: Session = Depends(get_db)):
    return ApiResponse(
        success=True,
        message="System analytics and reports generated",
        data={
            "fulfillment_rate": "92.4%",
            "average_match_score": "88/100",
            "average_donor_response_time": "11.5 minutes",
            "total_lives_impacted": 142
        }
    )

@router.put("/users/{id}/status", response_model=ApiResponse, dependencies=[admin_only])
def toggle_user_status(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return ApiResponse(success=True, message=f"User status set to active={user.is_active}")

@router.put("/donors/{id}/verify", response_model=ApiResponse, dependencies=[admin_only])
def verify_donor(id: int, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")
    donor.verified = True
    db.commit()
    return ApiResponse(success=True, message="Donor status set to verified")

@router.put("/hospitals/{id}/verify", response_model=ApiResponse, dependencies=[admin_only])
def verify_hospital(id: int, db: Session = Depends(get_db)):
    h = db.query(Hospital).filter(Hospital.id == id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    h.verified = True
    db.commit()
    return ApiResponse(success=True, message="Hospital verified successfully")

@router.put("/pharmacies/{id}/verify", response_model=ApiResponse, dependencies=[admin_only])
def verify_pharmacy(id: int, db: Session = Depends(get_db)):
    p = db.query(Pharmacy).filter(Pharmacy.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pharmacy not found")
    p.verified = True
    db.commit()
    return ApiResponse(success=True, message="Pharmacy verified successfully")
