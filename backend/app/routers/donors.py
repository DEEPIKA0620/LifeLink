from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.donor import Donor
from app.models.donation_history import DonationHistory
from app.utils.distance import calculate_haversine_distance, estimate_travel_time_minutes, format_travel_time_label
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
    lat: float = Query(..., description="Latitude of search origin"),
    lon: float = Query(..., description="Longitude of search origin"),
    blood_group: Optional[str] = Query(None, description="Blood group or 'ALL' for all blood groups"),
    radius_km: float = Query(25.0, description="Search radius in kilometers (5, 10, 15, 25, 50)"),
    availability: Optional[str] = Query("available", description="'available', 'unavailable', 'busy', or 'all'"),
    verified: Optional[str] = Query("true", description="'true' for verified only, 'all' for any"),
    sort: Optional[str] = Query("nearest", description="'nearest', 'response_rate', or 'donations'"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Geospatial donor search using Haversine formula calculation.
    Supports filtering by blood group (or all groups), availability, verified status, and distance radius.
    Estimated travel time assumes 30 km/h average speed without faking traffic telemetry.
    """
    query = db.query(Donor)

    # Verification filter
    if verified and verified.lower() == "true":
        query = query.filter(Donor.verified == True)

    # Availability filter
    if availability and availability.lower() not in ["all", "any"]:
        query = query.filter(Donor.availability_status == availability.lower())

    # Blood group filter: if None, empty, or "ALL", do not filter by blood group!
    if blood_group and blood_group.strip().upper() not in ["", "ALL", "ALL BLOOD GROUPS", "ANY"]:
        query = query.filter(Donor.blood_group == blood_group.strip().upper())

    all_donors = query.all()
    nearby_list = []

    for d in all_donors:
        if d.latitude is None or d.longitude is None:
            continue
        d_lat = d.latitude
        d_lon = d.longitude

        dist = calculate_haversine_distance(lat, lon, d_lat, d_lon)
        
        if dist <= radius_km:
            est_mins = estimate_travel_time_minutes(dist)
            nearby_list.append({
                "id": d.id,
                "user_id": d.user_id,
                "full_name": d.user.full_name if d.user else f"Donor #{d.id}",
                "blood_group": d.blood_group,
                "availability_status": d.availability_status,
                "verified": d.verified,
                "city": d.city,
                "locality": getattr(d, "locality", None) or (d.user.address if d.user else d.city),
                "distance_km": dist,
                "estimated_minutes": est_mins,
                "travel_time_label": format_travel_time_label(est_mins),
                "response_rate": d.response_rate,
                "total_donations": d.total_donations,
                "last_donation_date": d.last_donation_date.isoformat() if d.last_donation_date else None,
                "latitude": d.latitude,
                "longitude": d.longitude
            })

    # Sorting
    if sort == "response_rate":
        nearby_list.sort(key=lambda x: (x["response_rate"], -x["distance_km"]), reverse=True)
    elif sort == "donations":
        nearby_list.sort(key=lambda x: (x["total_donations"], -x["distance_km"]), reverse=True)
    else: # default: nearest distance
        nearby_list.sort(key=lambda x: x["distance_km"])

    paged_results = nearby_list[:limit]

    return ApiResponse(
        success=True,
        message=f"Found {len(nearby_list)} matching donors within {radius_km} km",
        data={
            "donors": paged_results,
            "total_found": len(nearby_list),
            "radius_km": radius_km,
            "origin": {"lat": lat, "lon": lon}
        }
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

@router.get("/me/requests", response_model=ApiResponse)
def get_donor_matched_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["donor", "admin"]))
):
    """
    Returns emergency requests relevant to the logged-in donor,
    including the donor's individual response status ('pending', 'accepted', 'rejected').
    """
    from app.models.blood_request import BloodRequest
    from app.models.donor_match import DonorMatch

    donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()

    requests = db.query(BloodRequest).filter(
        BloodRequest.status.in_(["searching", "donor_notified", "donor_accepted"])
    ).order_by(BloodRequest.created_at.desc()).all()

    results = []
    for r in requests:
        my_status = "pending"
        match_id = None
        if donor:
            match = db.query(DonorMatch).filter(
                DonorMatch.request_id == r.id,
                DonorMatch.donor_id == donor.id
            ).first()
            if match:
                my_status = match.status
                match_id = match.id

        results.append({
            "id": r.id,
            "match_id": match_id,
            "blood_group": r.blood_group,
            "units_required": r.units_required,
            "priority": r.priority,
            "hospital_name": r.hospital_name,
            "required_by": r.required_by.isoformat() if r.required_by else None,
            "status": r.status,
            "my_status": my_status
        })

    return ApiResponse(
        success=True,
        message=f"Loaded {len(results)} emergency requests",
        data={"requests": results}
    )
