import sqlite3
import os
import requests
import json
import time

SUPABASE_URL = "https://loznqcvfnrodrpaifsfk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvem5xY3ZmbnJvZHJwYWlmc2ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI4Mzk1ODIsImV4cCI6MjEwODQxNTU4Mn0.Cs0z86dcAEkRJz0ndm0cOPE8F-l-f4gVenZAFuQjY8g"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "lifelink.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

tables_sync = [
    ("users", ["id", "full_name", "email", "phone", "password_hash", "role", "address", "city", "latitude", "longitude", "is_active", "created_at", "updated_at"]),
    ("hospitals", ["id", "user_id", "hospital_name", "registration_number", "phone", "address", "city", "latitude", "longitude", "verified", "created_at", "updated_at"]),
    ("pharmacies", ["id", "user_id", "pharmacy_name", "phone", "address", "city", "latitude", "longitude", "opening_time", "closing_time", "verified", "created_at", "updated_at"]),
    ("donors", ["id", "user_id", "blood_group", "date_of_birth", "last_donation_date", "availability_status", "latitude", "longitude", "city", "locality", "response_rate", "total_donations", "verified", "created_at", "updated_at"]),
    ("blood_stock", ["id", "hospital_id", "blood_group", "units_available", "low_stock_threshold", "last_updated", "created_at"]),
    ("medicines", ["id", "pharmacy_id", "medicine_name", "generic_name", "category", "dosage_form", "strength", "quantity", "unit", "price", "availability_status", "last_updated", "created_at", "updated_at"]),
    ("blood_requests", ["id", "requester_id", "hospital_id", "blood_group", "units_required", "priority", "required_by", "latitude", "longitude", "hospital_name", "additional_notes", "status", "created_at", "updated_at"]),
    ("donor_matches", ["id", "request_id", "donor_id", "match_score", "distance_km", "estimated_minutes", "blood_compatibility", "availability_score", "distance_score", "response_score", "eligibility_score", "match_reasons", "status", "created_at", "updated_at"]),
    ("donation_history", ["id", "donor_id", "hospital_id", "request_id", "donation_date", "blood_group", "units", "status", "donation_type", "notes", "created_at", "updated_at"])
]

bool_cols = {"is_active", "verified"}
batch_size = 100

print("=== Starting Supabase Synchronization ===")

for tbl, cols in tables_sync:
    cursor.execute(f"SELECT * FROM {tbl} ORDER BY id ASC;")
    rows = cursor.fetchall()
    total = len(rows)
    print(f"Syncing table '{tbl}' ({total} rows)...")
    
    # Process in batches
    for i in range(0, total, batch_size):
        chunk = rows[i:i + batch_size]
        payload = []
        for r in chunk:
            item = {}
            date_cols = {"date_of_birth", "last_donation_date", "required_by", "last_updated", "created_at", "updated_at", "donation_date"}
            fk_nullable = {"hospital_id", "request_id", "reference_id"}
            for c in cols:
                if c in r.keys():
                    val = r[c]
                    if c in bool_cols:
                        item[c] = bool(val) if val is not None else False
                    elif c in date_cols and val == "":
                        item[c] = None
                    elif c in fk_nullable and (val == "" or val is None):
                        item[c] = None
                    elif val is None and c in ("address", "city", "locality", "additional_notes", "notes", "notes"):
                        # If column allows null or requires empty string
                        item[c] = ""
                    else:
                        item[c] = val
            payload.append(item)
            
        url = f"{SUPABASE_URL}/rest/v1/{tbl}"
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        if resp.status_code not in (200, 201, 204):
            print(f"ERROR syncing {tbl} rows {i} to {i+len(chunk)}: {resp.status_code}")
            print(f"Response: {resp.text}")
            conn.close()
            exit(1)
        time.sleep(0.05) # small throttle
        
    print(f"  [OK] Successfully synced {total} rows to '{tbl}'.")

conn.close()
print("=== All tables synchronized successfully! ===")
