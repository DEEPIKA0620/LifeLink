import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "lifelink.db")
sql_path = os.path.join(os.path.dirname(__file__), "supabase_seed_expanded.sql")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

output_lines = [
    "-- LifeLink Expanded Dataset Seed Script (PostgreSQL / Supabase)",
    "-- Contains 686 Users, 591 Donors (All 8 Blood Groups, 15 Cities), 41 Hospitals, 45 Pharmacies,",
    "-- 1300+ Medicines, Blood Stock, Requests, Matches, and 250 Donation History Records.",
    "-- Default Password for all seed users: LifeLink@123",
    "-- Idempotent using ON CONFLICT DO NOTHING.",
    "",
    "SET statement_timeout = 0;",
    "SET client_encoding = 'UTF8';",
    ""
]

def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    # String
    s = str(val).replace("'", "''")
    return f"'{s}'"

tables_order = [
    ("users", ["id", "full_name", "email", "phone", "password_hash", "role", "address", "city", "latitude", "longitude", "is_active", "created_at"]),
    ("hospitals", ["id", "user_id", "hospital_name", "registration_number", "phone", "address", "city", "latitude", "longitude", "verified", "created_at"]),
    ("pharmacies", ["id", "user_id", "pharmacy_name", "phone", "address", "city", "latitude", "longitude", "opening_time", "closing_time", "verified", "created_at"]),
    ("donors", ["id", "user_id", "blood_group", "date_of_birth", "last_donation_date", "availability_status", "latitude", "longitude", "city", "locality", "response_rate", "total_donations", "verified", "created_at"]),
    ("blood_stock", ["id", "hospital_id", "blood_group", "units_available", "low_stock_threshold", "last_updated", "created_at"]),
    ("medicines", ["id", "pharmacy_id", "medicine_name", "generic_name", "category", "dosage_form", "strength", "quantity", "unit", "price", "availability_status", "last_updated", "created_at"]),
    ("blood_requests", ["id", "requester_id", "hospital_id", "blood_group", "units_required", "priority", "required_by", "latitude", "longitude", "hospital_name", "additional_notes", "status", "created_at"]),
    ("donor_matches", ["id", "request_id", "donor_id", "match_score", "distance_km", "estimated_minutes", "match_reasons", "status", "created_at"]),
    ("donation_history", ["id", "donor_id", "hospital_id", "request_id", "donation_date", "blood_group", "units", "status", "donation_type", "notes", "created_at"])
]

for tbl, cols in tables_order:
    cursor.execute(f"SELECT * FROM {tbl};")
    rows = cursor.fetchall()
    if not rows:
        continue

    output_lines.append(f"-- Table: {tbl} ({len(rows)} records)")
    col_names = ", ".join(cols)
    for r in rows:
        vals = []
        for c in cols:
            val = r[c] if c in r.keys() else None
            vals.append(escape_sql(val))
        val_str = ", ".join(vals)
        output_lines.append(f"INSERT INTO {tbl} ({col_names}) VALUES ({val_str}) ON CONFLICT DO NOTHING;")
    output_lines.append("")

with open(sql_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Exported expanded dataset to {sql_path} successfully!")
conn.close()
