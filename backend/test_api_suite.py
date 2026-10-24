import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_root():
    """Verify backend health and root endpoints"""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_demo_user_logins():
    """Verify all 5 role seed accounts can login with LifeLink@123"""
    roles_and_emails = [
        ("admin", "admin@lifelink.org"),
        ("patient", "patient1@example.com"),
        ("donor", "ravi.kumar@example.com"),
        ("hospital", "manipal@lifelink.org"),
        ("pharmacy", "apollopharm1@lifelink.org"),
    ]
    for role, email in roles_and_emails:
        res = client.post("/api/auth/login", json={
            "email": email,
            "password": "LifeLink@123"
        })
        assert res.status_code == 200, f"Failed for {email}: {res.text}"
        data = res.json()["data"]
        assert "access_token" in data
        assert data["user"]["role"] == role
        assert data["user"]["email"] == email

def test_invalid_login():
    """Verify failed login on bad credentials"""
    res = client.post("/api/auth/login", json={
        "email": "admin@lifelink.org",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

def test_registration_and_duplicate():
    """Verify registration, token issuance, and duplicate email prevention"""
    import random
    rand_id = random.randint(10000, 99999)
    email = f"testuser_{rand_id}@example.com"

    # Register
    res = client.post("/api/auth/register", json={
        "email": email,
        "password": "StrongPassword123!",
        "full_name": f"Test User {rand_id}",
        "phone": f"+9198765{rand_id % 100000:05d}",
        "role": "patient",
        "city": "Bangalore"
    })
    assert res.status_code == 201
    assert "access_token" in res.json()["data"]

    # Duplicate registration
    dup_res = client.post("/api/auth/register", json={
        "email": email,
        "password": "StrongPassword123!",
        "full_name": "Duplicate User",
        "phone": "+919999999999",
        "role": "patient"
    })
    assert dup_res.status_code in [400, 409]

def test_role_based_access_control():
    """Verify RBAC: Patients cannot access admin endpoints, Admins can"""
    # 1. Login as patient
    patient_res = client.post("/api/auth/login", json={
        "email": "patient1@example.com",
        "password": "LifeLink@123"
    })
    patient_token = patient_res.json()["data"]["access_token"]

    # Patient tries to access admin dashboard -> 403 Forbidden
    forbidden_res = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert forbidden_res.status_code == 403

    # 2. Login as admin
    admin_res = client.post("/api/auth/login", json={
        "email": "admin@lifelink.org",
        "password": "LifeLink@123"
    })
    admin_token = admin_res.json()["data"]["access_token"]

    # Admin accesses admin dashboard -> 200 OK
    admin_get = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_get.status_code == 200
    assert "stats" in admin_get.json()["data"]

def test_medicine_search():
    """Verify medicine search by name, generic name, and empty query"""
    # Search Paracetamol
    res = client.get("/api/medicines/search?q=Paracetamol")
    assert res.status_code == 200
    meds = res.json()["data"]["medicines"]
    assert len(meds) > 0
    assert any("Paracetamol" in m["medicine_name"] for m in meds)

    # Search Generic: Acetaminophen
    res_gen = client.get("/api/medicines/search?q=Acetaminophen")
    assert res_gen.status_code == 200
    assert len(res_gen.json()["data"]["medicines"]) > 0

    # Search with empty query should return full list without 422 error
    res_all = client.get("/api/medicines/search")
    assert res_all.status_code == 200
    assert len(res_all.json()["data"]["medicines"]) >= 10

def test_donor_search_and_matching():
    """Verify nearby donor search and emergency request flow"""
    # Search nearby donors around Bangalore
    res = client.get("/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km=30&blood_group=O%2B")
    assert res.status_code == 200
    donors = res.json()["data"]["donors"]
    assert len(donors) > 0

    # Patient creates an emergency request
    patient_res = client.post("/api/auth/login", json={
        "email": "patient1@example.com",
        "password": "LifeLink@123"
    })
    token = patient_res.json()["data"]["access_token"]

    req_payload = {
        "blood_group": "O+",
        "units_required": 2,
        "priority": "critical",
        "hospital_name": "Manipal Hospital",
        "hospital_address": "98 HAL Airport Rd, Bangalore",
        "latitude": 12.9589,
        "longitude": 77.6508,
        "contact_phone": "+919876543210",
        "notes": "Urgent surgery patient",
        "required_by": "2026-10-30T18:00:00"
    }

    req_res = client.post(
        "/api/blood-requests",
        json=req_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert req_res.status_code in [200, 201]
    req_data = req_res.json()["data"]
    request_id = req_data["id"]

    # Verify request matches
    matches_res = client.get(
        f"/api/blood-requests/{request_id}/matches",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert matches_res.status_code == 200
    matches = matches_res.json()["data"]["matches"]
    assert len(matches) > 0
    # Verify score transparency
    first_match = matches[0]
    assert "match_score" in first_match
    assert "distance_km" in first_match

def test_blood_stock_and_notifications():
    """Verify hospital blood stock query and notifications"""
    # Hospital blood stock
    stock_res = client.get("/api/blood-stock")
    assert stock_res.status_code == 200
    stocks = stock_res.json()["data"]["blood_stock"]
    assert len(stocks) > 0

    # Notifications for patient
    patient_res = client.post("/api/auth/login", json={
        "email": "patient1@example.com",
        "password": "LifeLink@123"
    })
    token = patient_res.json()["data"]["access_token"]

    notif_res = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert notif_res.status_code == 200
    assert "notifications" in notif_res.json()["data"]

def test_donor_profile_and_availability():
    """Verify donor profile updates and availability toggling"""
    login_res = client.post("/api/auth/login", json={
        "email": "ravi.kumar@example.com",
        "password": "LifeLink@123"
    })
    token = login_res.json()["data"]["access_token"]

    # Toggle to busy
    res_busy = client.put(
        "/api/donors/availability",
        json={"availability_status": "busy"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_busy.status_code == 200
    assert res_busy.json()["data"]["availability_status"] == "busy"

    # Toggle back to available
    res_avail = client.put(
        "/api/donors/availability",
        json={"availability_status": "available"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_avail.status_code == 200
    assert res_avail.json()["data"]["availability_status"] == "available"

    # Fetch donation history
    hist_res = client.get(
        "/api/donors/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert hist_res.status_code == 200
    assert "history" in hist_res.json()["data"]

def test_pharmacy_inventory_lifecycle():
    """Verify pharmacy adds new medicine, verifies it via search, and deletes it"""
    pharm_res = client.post("/api/auth/login", json={
        "email": "apollopharm1@lifelink.org",
        "password": "LifeLink@123"
    })
    token = pharm_res.json()["data"]["access_token"]

    # Add new medicine
    med_payload = {
        "medicine_name": "Test Azithromycin 500mg",
        "generic_name": "Azithromycin",
        "category": "Antibiotics",
        "quantity": 50,
        "unit": "tablets",
        "price": 120.0
    }
    create_res = client.post(
        "/api/medicines",
        json=med_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_res.status_code == 201
    med_id = create_res.json()["data"]["id"]

    # Verify search returns the new medicine
    search_res = client.get("/api/medicines/search?q=Azithromycin")
    assert search_res.status_code == 200
    meds = search_res.json()["data"]["medicines"]
    assert any(m["id"] == med_id for m in meds)

    # Delete medicine
    del_res = client.delete(
        f"/api/medicines/{med_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert del_res.status_code == 200

def test_hospital_blood_stock_update():
    """Verify hospital can update blood stock and persist changes"""
    hosp_res = client.post("/api/auth/login", json={
        "email": "manipal@lifelink.org",
        "password": "LifeLink@123"
    })
    token = hosp_res.json()["data"]["access_token"]

    # Update blood stock for O+
    update_res = client.post(
        "/api/blood-stock?blood_group=O%2B&units_available=42&low_stock_threshold=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_res.status_code in [200, 201]

    # Verify public stock reflects 42 units for Manipal Hospital
    stock_res = client.get("/api/blood-stock?blood_group=O%2B")
    assert stock_res.status_code == 200
    stocks = stock_res.json()["data"]["blood_stock"]
    manipal_o_plus = next((s for s in stocks if "Manipal" in s["hospital_name"] and s["blood_group"] == "O+"), None)
    assert manipal_o_plus is not None
    assert manipal_o_plus["units_available"] == 42

def test_locations_catalog_endpoint():
    """Verify /api/locations returns 15+ cities with coordinates and localities"""
    res = client.get("/api/locations")
    assert res.status_code == 200
    data = res.json()["data"]
    cities = data.get("cities", [])
    assert len(cities) >= 15
    city_names = [c["city"] for c in cities]
    for required in ["Chennai", "Coimbatore", "Madurai", "Bengaluru", "Hyderabad", "Mumbai", "Delhi"]:
        assert required in city_names
    for c in cities:
        assert "center" in c and "lat" in c["center"] and "lon" in c["center"]
        assert len(c["localities"]) > 0

def test_all_eight_blood_groups_and_all_filter():
    """Requirement 1 & 2: Verify all 8 blood groups can be searched and returned, plus 'ALL' filter"""
    groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    # Search across a wide radius covering Tamil Nadu and Karnataka
    for bg in groups:
        import urllib.parse
        encoded_bg = urllib.parse.quote(bg)
        res = client.get(f"/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km=50&blood_group={encoded_bg}&availability=all")
        assert res.status_code == 200, f"Failed for {bg}: {res.text}"
        donors = res.json()["data"]["donors"]
        assert len(donors) > 0, f"No donors found for {bg} within 50km of Bengaluru"
        for d in donors:
            assert d["blood_group"] == bg

    # Search with blood_group=ALL
    res_all = client.get("/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km=50&blood_group=ALL&availability=all")
    assert res_all.status_code == 200
    donors_all = res_all.json()["data"]["donors"]
    returned_groups = set(d["blood_group"] for d in donors_all)
    assert len(donors_all) >= 20
    assert len(returned_groups) >= 6, "Expected diverse blood groups in ALL search"

def test_radii_monotonicity_and_strict_bounds():
    """Requirement 3: Verify 5km, 10km, 15km, 25km, 50km searches strictly obey bounds"""
    radii = [5, 10, 15, 25, 50]
    counts = []

    for r in radii:
        res = client.get(f"/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km={r}&availability=all")
        assert res.status_code == 200
        donors = res.json()["data"]["donors"]
        counts.append(len(donors))
        for d in donors:
            assert d["distance_km"] <= float(r) + 0.05, f"Donor distance {d['distance_km']} exceeds radius {r}"

    # Verify monotonic expansion
    for i in range(len(counts) - 1):
        assert counts[i] <= counts[i + 1], f"Radius {radii[i]}km count ({counts[i]}) > radius {radii[i+1]}km count ({counts[i+1]})"

def test_multi_city_isolation():
    """Requirement 4: Searching from Chennai must NOT return Bengaluru donors (~290 km away)"""
    # Chennai Central coordinates: 13.0827, 80.2707
    res_chennai = client.get("/api/donors/nearby?lat=13.0827&lon=80.2707&radius_km=25&availability=all")
    assert res_chennai.status_code == 200
    chennai_donors = res_chennai.json()["data"]["donors"]
    assert len(chennai_donors) > 0, "Expected donors in Chennai within 25km"
    for d in chennai_donors:
        assert d["city"] == "Chennai", f"Unexpected non-Chennai donor {d['city']} found in 25km Chennai radius"
        assert d["distance_km"] <= 25.0

    # Coimbatore coordinates: 11.0168, 76.9558
    res_cbe = client.get("/api/donors/nearby?lat=11.0168&lon=76.9558&radius_km=25&availability=all")
    assert res_cbe.status_code == 200
    cbe_donors = res_cbe.json()["data"]["donors"]
    assert len(cbe_donors) > 0
    for d in cbe_donors:
        assert d["city"] == "Coimbatore"

def test_distance_sorting_and_travel_time():
    """Requirement 5: Test nearest-first sorting and transparent 30 km/h travel time calculation"""
    res = client.get("/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km=50&sort=nearest&availability=all")
    assert res.status_code == 200
    donors = res.json()["data"]["donors"]
    assert len(donors) >= 2

    # Verify distances are non-decreasing
    for i in range(len(donors) - 1):
        assert donors[i]["distance_km"] <= donors[i + 1]["distance_km"]

    # Verify 30 km/h baseline estimate: ~distance * 2 minutes
    import math
    for d in donors[:5]:
        expected_mins = max(2, int(math.ceil((d["distance_km"] / 30.0) * 60.0)))
        assert d["estimated_minutes"] == expected_mins
        assert "approx. 30 km/h estimate" in d["travel_time_label"]

def test_empty_donor_search_results():
    """Requirement 6: Verify clear empty state when searching coordinates in uninhabited area"""
    # Coordinates in middle of ocean: 0.0, 0.0 with 5km radius
    res = client.get("/api/donors/nearby?lat=0.0&lon=0.0&radius_km=5")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_found"] == 0
    assert len(data["donors"]) == 0

def test_medicine_multi_pharmacy_and_filters():
    """Requirement 7, 8 & 9: Test medicine name, generic name, multi-pharmacy stocking, price sort, and filters"""
    # Multiple pharmacies stock Paracetamol
    res = client.get("/api/medicines/search?q=Paracetamol")
    assert res.status_code == 200
    meds = res.json()["data"]["medicines"]
    assert len(meds) >= 5, "Expected multiple pharmacies to stock Paracetamol"
    pharmacy_names = set(m["pharmacy_name"] for m in meds)
    assert len(pharmacy_names) >= 3, "Expected at least 3 distinct pharmacies stocking Paracetamol"

    # Filter by category
    res_cat = client.get("/api/medicines/search?category=Antibiotics")
    assert res_cat.status_code == 200
    for m in res_cat.json()["data"]["medicines"][:10]:
        assert "Antibiotics" in m["category"]

    # Filter by dosage form
    res_dosage = client.get("/api/medicines/search?dosage_form=Tablet")
    assert res_dosage.status_code == 200
    for m in res_dosage.json()["data"]["medicines"][:10]:
        assert "Tablet" in m["dosage_form"]

    # Sort by price ascending
    res_price = client.get("/api/medicines/search?q=Paracetamol&sort=price_asc")
    assert res_price.status_code == 200
    p_meds = res_price.json()["data"]["medicines"]
    for i in range(len(p_meds) - 1):
        assert p_meds[i]["price"] <= p_meds[i + 1]["price"]

    # Distance calculation with origin coordinates
    res_dist = client.get("/api/medicines/search?q=Paracetamol&lat=12.9716&lon=77.5946&radius_km=25")
    assert res_dist.status_code == 200
    for m in res_dist.json()["data"]["medicines"]:
        assert m["distance_km"] is not None
        assert m["distance_km"] <= 25.0
        assert "approx. 30 km/h estimate" in m["travel_time_label"]

def test_comprehensive_donation_history_ledger():
    """Requirement 10: Test /api/donations with status tabs, KPI stats, blood group filter, and pagination"""
    admin_res = client.post("/api/auth/login", json={
        "email": "admin@lifelink.org",
        "password": "LifeLink@123"
    })
    token = admin_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch all records
    res = client.get("/api/donations", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]
    stats = data["stats"]
    assert stats["total_donations"] >= 200, f"Expected >= 200 donations, found {stats['total_donations']}"
    assert stats["completed"] > 0
    assert stats["scheduled"] > 0
    assert stats["cancelled"] > 0
    assert stats["total_units"] >= stats["completed"]

    # Filter by status = completed
    res_completed = client.get("/api/donations?status=completed", headers=headers)
    assert res_completed.status_code == 200
    comp_records = res_completed.json()["data"]["donations"]
    assert all(r["status"] == "completed" for r in comp_records)

    # Filter by status = scheduled
    res_scheduled = client.get("/api/donations?status=scheduled", headers=headers)
    assert res_scheduled.status_code == 200
    sched_records = res_scheduled.json()["data"]["donations"]
    assert all(r["status"] == "scheduled" for r in sched_records)

    # Filter by blood group = O+
    import urllib.parse
    res_bg = client.get(f"/api/donations?blood_group={urllib.parse.quote('O+')}", headers=headers)
    assert res_bg.status_code == 200
    bg_records = res_bg.json()["data"]["donations"]
    assert all(r["blood_group"] == "O+" for r in bg_records)

def test_blood_request_listing_and_donor_accept_reject():
    """Verify emergency requests listing doesn't crash with None dates and donor can accept/reject by request_id"""
    # 1. Listing blood requests publicly/for hospital/patient
    res = client.get("/api/blood-requests")
    assert res.status_code == 200
    requests = res.json()["data"]["requests"]
    assert len(requests) > 0
    test_req = requests[0]
    req_id = test_req["id"]

    # 2. Login as donor
    donor_res = client.post("/api/auth/login", json={
        "email": "ravi.kumar@example.com",
        "password": "LifeLink@123"
    })
    assert donor_res.status_code == 200
    donor_token = donor_res.json()["data"]["access_token"]
    donor_headers = {"Authorization": f"Bearer {donor_token}"}

    # 3. Donor requests endpoint /api/donors/me/requests
    me_reqs = client.get("/api/donors/me/requests", headers=donor_headers)
    assert me_reqs.status_code == 200
    assert "requests" in me_reqs.json()["data"]

    # 4. Donor accepts request
    accept_res = client.post(f"/api/blood-requests/{req_id}/accept", headers=donor_headers)
    assert accept_res.status_code == 200
    assert accept_res.json()["data"]["match_status"] == "accepted"

    # 5. Donor rejects request
    reject_res = client.post(f"/api/blood-requests/{req_id}/reject", headers=donor_headers)
    assert reject_res.status_code == 200
    assert reject_res.json()["data"]["match_status"] == "rejected"

