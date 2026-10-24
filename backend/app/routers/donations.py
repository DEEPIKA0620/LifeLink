from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional
from datetime import datetime, date
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.donor import Donor
from app.models.hospital import Hospital
from app.models.donation_history import DonationHistory
from app.schemas.auth import ApiResponse

router = APIRouter(prefix="/api/donations", tags=["Donations"])

@router.get("", response_model=ApiResponse)
def list_donation_records(
    donor_id: Optional[int] = None,
    blood_group: Optional[str] = None,
    donation_status: Optional[str] = Query(None, alias="status"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "newest",
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Comprehensive donation history endpoint with filters, summary KPIs, and pagination.
    Privacy rules enforced: Donors can only view their own history.
    """
    query = db.query(DonationHistory)

    # Privacy constraint
    if current_user.role == "donor":
        donor = db.query(Donor).filter(Donor.user_id == current_user.id).first()
        if not donor:
            return ApiResponse(
                success=True,
                message="No donor profile",
                data={"donations": [], "total": 0, "stats": {}}
            )
        query = query.filter(DonationHistory.donor_id == donor.id)
    elif donor_id is not None:
        query = query.filter(DonationHistory.donor_id == donor_id)

    # Status filter
    if donation_status and donation_status.lower() != "all":
        query = query.filter(DonationHistory.status == donation_status.lower())

    # Blood group filter
    if blood_group and blood_group.lower() != "all":
        query = query.filter(DonationHistory.blood_group == blood_group.upper())

    # Date range filters
    if from_date:
        try:
            d_from = datetime.strptime(from_date, "%Y-%m-%d").date()
            query = query.filter(DonationHistory.donation_date >= d_from)
        except ValueError:
            pass

    if to_date:
        try:
            d_to = datetime.strptime(to_date, "%Y-%m-%d").date()
            query = query.filter(DonationHistory.donation_date <= d_to)
        except ValueError:
            pass

    # Search filter (hospital name or donor notes)
    if search:
        search_term = f"%{search}%"
        query = query.join(Hospital, DonationHistory.hospital_id == Hospital.id, isouter=True).filter(
            or_(
                Hospital.hospital_name.ilike(search_term),
                DonationHistory.notes.ilike(search_term),
                DonationHistory.blood_group.ilike(search_term)
            )
        )

    # Overall KPIs for the matched donor/filter scope
    # Base query for metrics (without status filter applied to show complete tab counts)
    base_metric_query = db.query(DonationHistory)
    if current_user.role == "donor":
        base_metric_query = base_metric_query.filter(DonationHistory.donor_id == donor.id)
    elif donor_id is not None:
        base_metric_query = base_metric_query.filter(DonationHistory.donor_id == donor_id)

    all_records = base_metric_query.all()
    stats = {
        "total_donations": len(all_records),
        "completed": sum(1 for r in all_records if r.status == "completed"),
        "scheduled": sum(1 for r in all_records if r.status == "scheduled"),
        "cancelled": sum(1 for r in all_records if r.status == "cancelled"),
        "total_units": sum(r.units for r in all_records if r.status == "completed")
    }

    # Sorting
    if sort == "oldest":
        query = query.order_by(asc(DonationHistory.donation_date), asc(DonationHistory.id))
    else:
        query = query.order_by(desc(DonationHistory.donation_date), desc(DonationHistory.id))

    total_count = query.count()
    offset = (page - 1) * page_size
    records = query.offset(offset).limit(page_size).all()

    results = []
    for r in records:
        hosp = db.query(Hospital).filter(Hospital.id == r.hospital_id).first() if r.hospital_id else None
        donor_rec = db.query(Donor).filter(Donor.id == r.donor_id).first()
        results.append({
            "id": r.id,
            "donor_id": r.donor_id,
            "donor_display": f"Donor #{r.donor_id}" if current_user.role != "admin" and current_user.id != (donor_rec.user_id if donor_rec else None) else (donor_rec.user.full_name if donor_rec and donor_rec.user else f"Donor #{r.donor_id}"),
            "blood_group": r.blood_group,
            "donation_date": r.donation_date.isoformat() if r.donation_date else None,
            "hospital_id": r.hospital_id,
            "hospital_name": hosp.hospital_name if hosp else "LifeLink Mobile Center",
            "hospital_city": hosp.city if hosp else "Tamil Nadu",
            "request_id": r.request_id,
            "status": r.status or "completed",
            "units": r.units or 1,
            "donation_type": r.donation_type or "Whole Blood",
            "notes": r.notes or "Voluntary emergency blood donation",
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    return ApiResponse(
        success=True,
        message=f"Loaded {len(results)} donation records",
        data={
            "donations": results,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "stats": stats
        }
    )
