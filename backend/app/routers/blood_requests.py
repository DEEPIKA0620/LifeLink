from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.hospital import Hospital
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.audit_log import RequestStatusHistory
from app.services.matching_service import find_and_rank_donors
from app.services.notification_service import create_user_notification
from app.schemas.auth import ApiResponse
from app.schemas.blood_request import BloodRequestCreate, BloodRequestOut

router = APIRouter(prefix="/api/blood-requests", tags=["Blood Requests"])

@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_blood_request(
    req: BloodRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates an Emergency Blood Request, triggers Smart Donor Matching algorithm,
    creates notifications for top candidates, and returns ranked donor match list.
    """
    if req.units_required <= 0:
        raise HTTPException(status_code=400, detail="Units required must be greater than 0")

    # Save to blood_requests
    new_request = BloodRequest(
        requester_id=current_user.id,
        hospital_id=req.hospital_id,
        blood_group=req.blood_group.upper(),
        units_required=req.units_required,
        priority=req.priority.lower(),
        required_by=req.required_by,
        latitude=req.latitude or current_user.latitude or 12.9716,
        longitude=req.longitude or current_user.longitude or 77.5946,
        hospital_name=req.hospital_name,
        additional_notes=req.additional_notes,
        status="searching"
    )
    db.add(new_request)
    db.flush()

    # Add Status Timeline Entry
    status_entry = RequestStatusHistory(
        request_id=new_request.id,
        status="searching",
        changed_by=current_user.id,
        notes=f"Emergency blood request created for {req.units_required} unit(s) of {req.blood_group} ({req.priority.upper()})"
    )
    db.add(status_entry)
    db.commit()
    db.refresh(new_request)

    # Run Smart Donor Matching Algorithm
    matches = find_and_rank_donors(db, new_request, max_results=10)

    # Update request status & notify candidates
    if len(matches) > 0:
        new_request.status = "donor_notified"
        db.commit()

        # Send notifications to top matched donors
        for match in matches[:5]:
            donor_user_id = match["donor"].user_id
            score = match["match_score"]
            create_user_notification(
                db=db,
                user_id=donor_user_id,
                title=f"EMERGENCY BLOOD REQUEST ({new_request.priority.upper()})",
                message=f"Need {new_request.units_required} unit(s) of {new_request.blood_group} at {new_request.hospital_name}. Match Score: {score}/100.",
                notification_type="emergency_request",
                reference_id=new_request.id
            )

    return ApiResponse(
        success=True,
        message="Emergency blood request created successfully",
        data={
            "id": new_request.id,
            "request_id": new_request.id,
            "status": new_request.status,
            "blood_group": new_request.blood_group,
            "units_required": new_request.units_required,
            "matches_count": len(matches),
            "top_matches": [{
                "donor_id": m["donor_id"],
                "full_name": m["user_name"],
                "blood_group": m["blood_group"],
                "match_score": m["match_score"],
                "distance_km": m["distance_km"],
                "estimated_minutes": m["estimated_minutes"],
                "reasons": m["match_reasons"]
            } for m in matches[:5]]
        }
    )

@router.get("", response_model=ApiResponse)
def list_blood_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    blood_group: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(BloodRequest)
    if status_filter:
        query = query.filter(BloodRequest.status == status_filter)
    if blood_group:
        query = query.filter(BloodRequest.blood_group == blood_group.upper())
    if priority:
        query = query.filter(BloodRequest.priority == priority.lower())

    requests = query.order_by(BloodRequest.created_at.desc()).all()
    results = []
    for r in requests:
        results.append({
            "id": r.id,
            "requester_id": r.requester_id,
            "requester_name": r.requester.full_name if r.requester else "Patient",
            "hospital_name": r.hospital_name,
            "blood_group": r.blood_group,
            "units_required": r.units_required,
            "priority": r.priority,
            "required_by": r.required_by.isoformat() if r.required_by else None,
            "status": r.status,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return ApiResponse(success=True, message=f"Loaded {len(results)} blood requests", data={"requests": results})

@router.get("/{id}", response_model=ApiResponse)
def get_blood_request_detail(id: int, db: Session = Depends(get_db)):
    req = db.query(BloodRequest).filter(BloodRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Blood request not found")

    status_history = db.query(RequestStatusHistory).filter(RequestStatusHistory.request_id == id).order_by(RequestStatusHistory.created_at.asc()).all()

    return ApiResponse(
        success=True,
        message="Request detail loaded",
        data={
            "id": req.id,
            "requester_id": req.requester_id,
            "requester_name": req.requester.full_name if req.requester else "Patient",
            "requester_phone": req.requester.phone if req.requester else "",
            "hospital_name": req.hospital_name,
            "blood_group": req.blood_group,
            "units_required": req.units_required,
            "priority": req.priority,
            "required_by": req.required_by.isoformat() if req.required_by else None,
            "status": req.status,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "additional_notes": req.additional_notes,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "timeline": [{
                "status": sh.status,
                "notes": sh.notes,
                "timestamp": sh.created_at.isoformat() if sh.created_at else None
            } for sh in status_history]
        }
    )

@router.post("/{id}/cancel", response_model=ApiResponse)
def cancel_blood_request(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(BloodRequest).filter(BloodRequest.id == id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Blood request not found")

    if req.requester_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this request")

    req.status = "cancelled"
    
    # Timeline
    status_entry = RequestStatusHistory(
        request_id=req.id,
        status="cancelled",
        changed_by=current_user.id,
        notes="Blood request cancelled by user"
    )
    db.add(status_entry)
    db.commit()

    return ApiResponse(success=True, message="Blood request cancelled successfully")
