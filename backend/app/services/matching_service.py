from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.donor import Donor
from app.models.blood_request import BloodRequest
from app.models.donor_match import DonorMatch
from app.utils.blood_compatibility import is_blood_compatible
from app.utils.distance import calculate_haversine_distance, estimate_travel_time_minutes

def calculate_donor_match_score(donor: Donor, request: BloodRequest) -> Dict[str, Any]:
    """
    SMART EMERGENCY DONOR MATCHING ENGINE (100 Point Transparent Scoring):
    
    1. Blood Group Compatibility: 30 Points
    2. Availability Status: 20 Points
    3. Geographical Distance: 20 Points
    4. Estimated Travel Time: 10 Points
    5. Historical Response Rate: 10 Points
    6. Recorded Donation Eligibility: 10 Points
    
    Returns breakdown, total score (0-100), travel time, distance, and recommendation reasons.
    """
    reasons = []
    
    # 1. Blood Compatibility (30 Points)
    if is_blood_compatible(request.blood_group, donor.blood_group):
        compatibility_score = 30
        if donor.blood_group == request.blood_group:
            reasons.append(f"Exact match ({donor.blood_group})")
        else:
            reasons.append(f"Compatible donor group ({donor.blood_group} for {request.blood_group})")
    else:
        compatibility_score = 0

    # 2. Availability (20 Points)
    if donor.availability_status == "available":
        availability_score = 20
        reasons.append("Available now to donate")
    else:
        availability_score = 0
        reasons.append("Currently marked unavailable")

    # 3. Distance Score (20 Points)
    req_lat = request.latitude if request.latitude else 12.9716
    req_lon = request.longitude if request.longitude else 77.5946
    don_lat = donor.latitude if donor.latitude else req_lat
    don_lon = donor.longitude if donor.longitude else req_lon

    distance_km = calculate_haversine_distance(req_lat, req_lon, don_lat, don_lon)
    
    if distance_km <= 2.0:
        distance_score = 20
        reasons.append(f"Located very close ({distance_km:.1f} km)")
    elif distance_km <= 5.0:
        distance_score = 18
        reasons.append(f"Located within 5 km ({distance_km:.1f} km)")
    elif distance_km <= 10.0:
        distance_score = 14
        reasons.append(f"Located within 10 km ({distance_km:.1f} km)")
    elif distance_km <= 25.0:
        distance_score = 8
    else:
        distance_score = 3

    # 4. Travel Time Score (10 Points)
    estimated_minutes = estimate_travel_time_minutes(distance_km)
    if estimated_minutes <= 10:
        travel_score = 10
        reasons.append(f"Quick estimated arrival (~{estimated_minutes} mins)")
    elif estimated_minutes <= 25:
        travel_score = 8
    elif estimated_minutes <= 45:
        travel_score = 5
    else:
        travel_score = 2

    # 5. Response Rate Score (10 Points)
    donor_response_rate = donor.response_rate if donor.response_rate is not None else 100.0
    if donor_response_rate >= 90.0:
        response_score = 10
        reasons.append("High response rate")
    elif donor_response_rate >= 75.0:
        response_score = 8
    elif donor_response_rate >= 50.0:
        response_score = 5
    else:
        response_score = 2

    # 6. Donation Eligibility (10 Points)
    if donor.last_donation_date:
        days_since_last = (date.today() - donor.last_donation_date).days
        if days_since_last >= 90:
            eligibility_score = 10
            reasons.append("Recorded donation history indicates full eligibility")
        elif days_since_last >= 60:
            eligibility_score = 5
        else:
            eligibility_score = 2
            reasons.append("Recent donation recorded within last 60 days")
    else:
        eligibility_score = 10
        reasons.append("First-time / fully eligible donor record")

    # Calculate Total Match Score
    total_score = (
        compatibility_score +
        availability_score +
        distance_score +
        travel_score +
        response_score +
        eligibility_score
    )

    # Incompatible donors cannot have high score
    if compatibility_score == 0:
        total_score = min(total_score, 15)

    return {
        "match_score": total_score,
        "distance_km": distance_km,
        "estimated_minutes": estimated_minutes,
        "blood_compatibility": compatibility_score,
        "availability_score": availability_score,
        "distance_score": distance_score,
        "response_score": response_score,
        "eligibility_score": eligibility_score,
        "match_reasons": " | ".join(reasons)
    }

def find_and_rank_donors(db: Session, request: BloodRequest, max_results: int = 15) -> List[Dict[str, Any]]:
    """
    Finds candidates, calculates scores, ranks them, and stores matches in database.
    """
    all_donors = db.query(Donor).filter(Donor.verified == True).all()
    
    scored_matches = []
    for donor in all_donors:
        # Filter for basic compatibility
        if not is_blood_compatible(request.blood_group, donor.blood_group):
            continue
            
        score_data = calculate_donor_match_score(donor, request)
        
        scored_matches.append({
            "donor": donor,
            "donor_id": donor.id,
            "user_name": donor.user.full_name if donor.user else "Anonymous Donor",
            "blood_group": donor.blood_group,
            "availability_status": donor.availability_status,
            **score_data
        })

    # Sort by match_score descending, then distance_km ascending
    scored_matches.sort(key=lambda x: (-x["match_score"], x["distance_km"]))
    top_matches = scored_matches[:max_results]

    # Save to donor_matches table
    for match_item in top_matches:
        existing = db.query(DonorMatch).filter(
            DonorMatch.request_id == request.id,
            DonorMatch.donor_id == match_item["donor_id"]
        ).first()

        if not existing:
            db_match = DonorMatch(
                request_id=request.id,
                donor_id=match_item["donor_id"],
                match_score=match_item["match_score"],
                distance_km=match_item["distance_km"],
                estimated_minutes=match_item["estimated_minutes"],
                blood_compatibility=match_item["blood_compatibility"],
                availability_score=match_item["availability_score"],
                distance_score=match_item["distance_score"],
                response_score=match_item["response_score"],
                eligibility_score=match_item["eligibility_score"],
                match_reasons=match_item["match_reasons"],
                status="notified"
            )
            db.add(db_match)
    
    db.commit()
    return top_matches
