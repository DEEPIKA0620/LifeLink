import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.main import app

client = TestClient(app)

def test_api_docs():
    """Verify OpenAPI Swagger documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_login_demo_admin():
    """Test login with demo admin credentials."""
    payload = {
        "email": "admin@lifelink.org",
        "password": "LifeLink@123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"

def test_login_invalid_credentials():
    """Test login failure with invalid password."""
    payload = {
        "email": "admin@lifelink.org",
        "password": "WrongPassword123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code in [400, 401]

def test_login_demo_patient_and_me_endpoint():
    """Test login as patient and retrieving '/api/auth/me' profile."""
    login_res = client.post("/api/auth/login", json={
        "email": "patient1@example.com",
        "password": "LifeLink@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    res_data = me_res.json()
    assert res_data["success"] is True
    user_data = res_data["data"]
    assert user_data["email"] == "patient1@example.com"
    assert user_data["role"] == "patient"

def test_get_nearby_donors():
    """Test finding nearby donors with lat/lon parameters."""
    response = client.get("/api/donors/nearby?lat=12.9716&lon=77.5946&radius_km=50")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    donors = res_data["data"]["donors"]
    assert isinstance(donors, list)
    assert len(donors) > 0

def test_search_medicines():
    """Test medicine search endpoint."""
    response = client.get("/api/medicines/search?q=Paracetamol")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    results = res_data["data"]["medicines"]
    assert isinstance(results, list)
    assert len(results) > 0
    assert "Paracetamol" in results[0]["medicine_name"]

def test_nearby_medicines():
    """Test finding nearby medicines with location coordinates."""
    response = client.get("/api/medicines/nearby?q=Paracetamol&lat=12.9716&lon=77.5946&radius_km=25")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    results = res_data["data"]["medicines"]
    assert isinstance(results, list)

def test_get_nearby_hospitals():
    """Test fetching nearby hospital blood banks."""
    response = client.get("/api/hospitals/nearby?lat=12.9716&lon=77.5946")
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    hospitals = res_data["data"]["hospitals"]
    assert isinstance(hospitals, list)
    assert len(hospitals) > 0

def test_admin_dashboard_stats():
    """Test admin dashboard statistics endpoint with admin authorization."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@lifelink.org",
        "password": "LifeLink@123"
    })
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/admin/dashboard", headers=headers)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    stats = res_data["data"]
    assert "stats" in stats
    assert "total_users" in stats["stats"]

def test_emergency_blood_request_workflow():
    """Test creating blood request and donor matching algorithm."""
    # 1. Login as patient
    login_res = client.post("/api/auth/login", json={
        "email": "patient1@example.com",
        "password": "LifeLink@123"
    })
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create emergency request
    required_time = (datetime.now() + timedelta(days=1)).isoformat()
    req_payload = {
        "blood_group": "O+",
        "units_required": 2,
        "priority": "critical",
        "required_by": required_time,
        "hospital_name": "Manipal Hospital",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "additional_notes": "Urgent test request"
    }

    create_res = client.post("/api/blood-requests", json=req_payload, headers=headers)
    assert create_res.status_code in [200, 201], create_res.text
    res_data = create_res.json()
    assert res_data["success"] is True
    req_data = res_data["data"]
    assert "request_id" in req_data
    assert req_data["matches_count"] >= 0
    request_id = req_data["request_id"]

    # 3. Fetch blood request details
    detail_res = client.get(f"/api/blood-requests/{request_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["success"] is True
    assert detail_data["data"]["blood_group"] == "O+"
