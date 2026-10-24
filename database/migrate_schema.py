import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "backend", "lifelink.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, col_type):
    cursor.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cursor.fetchall()]
    if column not in cols:
        print(f"Adding {column} ({col_type}) to {table}...")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type};")
        conn.commit()
    else:
        print(f"Column {column} already exists in {table}.")

# Donors
add_column_if_not_exists("donors", "locality", "VARCHAR(100)")

# Medicines
add_column_if_not_exists("medicines", "dosage_form", "VARCHAR(50)")
add_column_if_not_exists("medicines", "strength", "VARCHAR(50)")

# Donation History
add_column_if_not_exists("donation_history", "request_id", "INTEGER REFERENCES blood_requests(id)")
add_column_if_not_exists("donation_history", "status", "VARCHAR(20) DEFAULT 'completed'")
add_column_if_not_exists("donation_history", "donation_type", "VARCHAR(50) DEFAULT 'Whole Blood'")
add_column_if_not_exists("donation_history", "updated_at", "DATETIME")

# Create Indexes
indexes = [
    ("idx_donors_blood_group", "donors(blood_group)"),
    ("idx_donors_city", "donors(city)"),
    ("idx_donors_locality", "donors(locality)"),
    ("idx_donors_availability", "donors(availability_status)"),
    ("idx_medicines_name", "medicines(medicine_name)"),
    ("idx_medicines_generic", "medicines(generic_name)"),
    ("idx_medicines_category", "medicines(category)"),
    ("idx_medicines_status", "medicines(availability_status)"),
    ("idx_donation_history_status", "donation_history(status)"),
    ("idx_donation_history_donor", "donation_history(donor_id)"),
]

for idx_name, idx_target in indexes:
    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_target};")
conn.commit()

print("SQLite schema migration completed successfully!")
conn.close()
