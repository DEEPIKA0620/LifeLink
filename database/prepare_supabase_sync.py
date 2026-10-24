import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "lifelink.db")
output_dir = os.path.join(os.path.dirname(__file__), "supabase_batches")
os.makedirs(output_dir, exist_ok=True)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def escape_sql(col_name, val):
    if val is None:
        return "NULL"
    if col_name in ["is_active", "verified"]:
        return "TRUE" if bool(val) else "FALSE"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float)):
        return str(val)
    # Strings
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

batch_files = []
batch_size = 200

for tbl_idx, (tbl, cols) in enumerate(tables_order, start=1):
    cursor.execute(f"SELECT * FROM {tbl} ORDER BY id ASC;")
    rows = cursor.fetchall()
    if not rows:
        continue
    
    col_names = ", ".join(cols)
    total_rows = len(rows)
    num_batches = (total_rows + batch_size - 1) // batch_size
    
    for b in range(num_batches):
        batch_rows = rows[b * batch_size : (b + 1) * batch_size]
        values_list = []
        for r in batch_rows:
            vals = []
            for c in cols:
                val = r[c] if c in r.keys() else None
                vals.append(escape_sql(c, val))
            values_list.append(f"({', '.join(vals)})")
        
        sql_content = f"INSERT INTO {tbl} ({col_names}) VALUES\n" + ",\n".join(values_list) + "\nON CONFLICT (id) DO NOTHING;\n"
        
        filename = f"{tbl_idx:02d}_{tbl}_part{b+1}.sql"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(sql_content)
        batch_files.append((filename, len(batch_rows)))

print(f"Generated {len(batch_files)} batch files in {output_dir}")
for f, cnt in batch_files:
    print(f"  {f}: {cnt} rows")

conn.close()
