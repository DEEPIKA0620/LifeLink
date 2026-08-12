from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.donor import Donor
from app.models.donation_history import DonationHistory
from app.utils.distance import calculate_haversine_distance, estimate_travel_time_minutes
from app.schemas.auth import ApiResponse
from app.schemas.donor import DonorProfileUpdate, AvailabilityUpdate

router = APIRouter(prefix="/api/donors", tags=["Donors"])

@router.get("", response_model=ApiResponse)
def list_donors(
    blood_group: Optional[str] = None,
    city: Optional[str] = None,
    availability: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Donor).filter(Donor.verified == True)
    
    if blood_group:
        query = query.filter(Donor.blood_group == blood_group.upper())
    if city:
        query = query.filter(Donor.city.ilike(f"%{city}%"))
    if availability:
        query = query.filter(Donor.availability_status == availability)

    donors = query.all()
    results = []
    for d in donors:
        # Hide phone number unless explicitly authorized in donor acceptance flow
        results.append({
            "id": d.id,
            "user_id": d.user_id,
            "full_name": d.user.full_name if d.user else "Donor",
            "blood_group": d.blood_group,
            "availability_status": d.availability_status,
            "city": d.city,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "response_rate": d.response_rate,
            "total_donations": d.total_donations,
            "last_donation_date": d.last_donation_date.isoformat() if d.last_donation_date else None
        })

    return ApiResponse(success=True, message=f"Found {len(results)} donors", data={"donors": results})

@router.get("/nearby", response_model=ApiResponse)
def search_nearby_donors(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    blood_group: Optional[str] = None,
    radius_km: float = Query(25.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Location-based donor search using Haversine formula calculation in Python/MySQL.
    """
    query = db.query(Donor).filter(Donor.verified == True, Donor.availability_status == "available")
    if blood_group:
        query = query.filter(Donor.blood_group == blood_group.upper())

    all_donors = query.all()
    nearby_list = []

    for d in all_donors:
        d_lat = d.latitude if d.latitude else lat
        d_lon = d.longitude if d.longitude else lon
        dist = calculate_haversine_distance(lat, lon, d_lat, d_lon)
        
        if dist <= radius_km:
            est_mins = estimate_travel_time_minutes(dist)
            nearby_list.append({
                "id": d.id,
                "user_id": d.user_id,
                "full_name": d.user.full_name if d.user else "Donor",
                "blood_group": d.blood_group,
                "availability_status": d.availability_status,
                "city": d.city,
                "distance_km": dist,
                "estimated_minutes": est_mins,
                "response_rate": d.response_rate,
                "total_donations": d.total_donations,
                "latitude": d.latitude,
                "longitude": d.longitude
            })

    nearby_list.sort(key=lambda x: x["distance_km"])
    return ApiResponse(
        success=True,
        message=f"Found {len(nearby_list)} donors within {radius_km} km",
        data={"donors": nearby_list}
    )

@router.get("/{id}", response_model=ApiResponse)
def get_donor_detail(id: int, db: Session = Depends(get_db)):
    donor = db.query(Donor).filter(Donor.id == id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor record not found")

    return ApiResponse(
        success=True,
        message="Donor details retrieved",
        data={
            "id": donor.id,
            "full_name": donor.user.full_name if donor.user else "Donor",
            "blood_group": donor.blood_group,
            "city": donor.city,
            "availability_status": donor.availability_status,
            "response_rate": donor.response_rate,
            "total_donations": donor.total_donations,
            "verified": donor.verified,
            "last_donation_date": donor.last_donation_date.isoformat() if donor.last_donation_date else None
        }
    )

@router.put("/profile", response_model=ApiResponse)
def update_donor_profile(
    req: DonorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["donor"]))
):
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    if req.blood_group:
        donor.blood_group = req.blood_group.upper()
    if req.last_donation_date:
        donor.last_donation_date = req.last_donation_date
    if req.availability_status:
        donor.availability_status = req.availability_status
    if req.city:
        donor.city = req.city
    if req.latitude:
        donor.latitude = req.latitude
    if req.longitude:
        donor.longitude = req.longitude

    db.commit()
    db.refresh(donor)
    return ApiResponse(success=True, message="Donor profile updated successfully")

@router.put("/availability", response_model=ApiResponse)
def toggle_donor_availability(
    req: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["donor"]))
):
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found")

    donor.availability_status = req.availability_status.lower()
    db.commit()
    return ApiResponse(
        success=True,
        message=f"Availability status set to {donor.availability_status}",
        data={"availability_status": donor.availability_status}
    )

@router.get("/history", response_model=ApiResponse)
def get_donation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["donor"]))
):
    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="Donor record not found")

    history = db.query(DonationHistory).filter(DonationHistory.donor_id == donor.id).all()
    results = [{
        "id": h.id,
        "donation_date": h.donation_date.isoformat(),
        "blood_group": h.blood_group,
        "units": h.units,
        "hospital_name": h.hospital.hospital_name if h.hospital else "Blood Bank Center",
        "notes": h.notes
    } for h in history]

    return ApiResponse(success=True, message="Donation history loaded", data={"history": results})
