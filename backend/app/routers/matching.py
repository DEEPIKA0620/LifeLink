from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.blood_request import BloodRequest
from app.models.donor_match import DonorMatch
from app.models.donation_history import DonationHistory
from app.models.audit_log import RequestStatusHistory
from app.services.matching_service import find_and_rank_donors
from app.services.notification_service import create_user_notification
from app.schemas.auth import ApiResponse

router = APIRouter(tags=["Donor Matching"])

@router.get("/api/blood-requests/{request_id}/matches", response_model=ApiResponse)
def get_request_matches(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns ranked candidate donor matches for a given emergency request.
    Includes privacy enforcement: phone numbers are hidden unless status is 'accepted'.
    """
    req = db.query(BloodRequest).filter(BloodRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Blood request not found")

    matches = db.query(DonorMatch).filter(DonorMatch.request_id == request_id).order_by(DonorMatch.match_score.desc()).all()
    
    results = []
    for m in matches:
        donor = db.query(Donor).filter(Donor.id == m.donor_id).first()
        if not donor:
            continue
            
        donor_user = db.query(User).filter(User.id == donor.user_id).first()
        
        # Privacy check: Contact details revealed ONLY if match status is 'accepted'
        # or if user is viewing their own profile/admin
        show_contact = (m.status == "accepted") or (current_user.role == "admin") or (current_user.id == donor.user_id)

        results.append({
            "match_id": m.id,
            "request_id": m.request_id,
            "donor_id": m.donor_id,
            "donor_name": donor_user.full_name if donor_user else "Available Donor",
            "donor_phone": donor_user.phone if (donor_user and show_contact) else "Hidden until donor accepts",
            "contact_revealed": show_contact,
            "blood_group": donor.blood_group,
            "match_score": m.match_score,
            "distance_km": float(m.distance_km),
            "estimated_minutes": m.estimated_minutes,
            "blood_compatibility_score": m.blood_compatibility,
            "availability_score": m.availability_score,
            "distance_score": m.distance_score,
            "response_score": m.response_score,
            "eligibility_score": m.eligibility_score,
            "match_reasons": m.match_reasons.split(" | ") if m.match_reasons else [],
            "status": m.status,
            "created_at": m.created_at.isoformat()
        })

    return ApiResponse(
        success=True,
        message=f"Found {len(results)} matches for blood request #{request_id}",
        data={"matches": results}
    )

@router.post("/api/blood-requests/{request_id}/match", response_model=ApiResponse)
def trigger_manual_rematch(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(BloodRequest).filter(BloodRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Blood request not found")

    matches = find_and_rank_donors(db, req)
    return ApiResponse(
        success=True,
        message=f"Smart Donor Matching executed. Generated {len(matches)} matches.",
        data={"matches_count": len(matches)}
    )

@router.post("/api/matches/{match_id}/accept", response_model=ApiResponse)
def accept_donor_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Donor accepts emergency request match.
    Updates match status to 'accepted', unlocks contact info for patient/hospital,
    creates notifications, and logs history.
    """
    match = db.query(DonorMatch).filter(DonorMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Donor match record not found")

    donor = db.query(Donor).filter(Donor.id == match.donor_id).first()
    if not donor or (donor.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Only the matched donor can accept this request")

    match.status = "accepted"

    req = db.query(BloodRequest).filter(BloodRequest.id == match.request_id).first()
    if req:
        req.status = "donor_accepted"
        
        # Timeline
        status_entry = RequestStatusHistory(
            request_id=req.id,
            status="donor_accepted",
            changed_by=current_user.id,
            notes=f"Donor {current_user.full_name} accepted the blood request"
        )
        db.add(status_entry)

        # Notify Requester
        create_user_notification(
            db=db,
            user_id=req.requester_id,
            title="DONOR ACCEPTED YOUR REQUEST",
            message=f"Donor {current_user.full_name} ({donor.blood_group}) accepted your blood request for {req.hospital_name}. Contact phone is now available.",
            notification_type="donor_accepted",
            reference_id=req.id
        )

    # Record donation entry
    donation = DonationHistory(
        donor_id=donor.id,
        hospital_id=req.hospital_id if req else None,
        donation_date=datetime.now().date(),
        blood_group=donor.blood_group,
        units=req.units_required if req else 1,
        notes=f"Donation accepted for request #{req.id}" if req else "Accepted donation"
    )
    db.add(donation)
    donor.total_donations += 1

    db.commit()

    return ApiResponse(
        success=True,
        message="Emergency blood request accepted successfully! Requester can now view your contact details.",
        data={"match_status": "accepted", "contact_phone": current_user.phone}
    )

@router.post("/api/matches/{match_id}/reject", response_model=ApiResponse)
def reject_donor_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    match = db.query(DonorMatch).filter(DonorMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Donor match record not found")

    donor = db.query(Donor).filter(Donor.id == match.donor_id).first()
    if not donor or (donor.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to reject this request match")

    match.status = "rejected"
    db.commit()

    return ApiResponse(success=True, message="Request match rejected")
