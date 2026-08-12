import re
from typing import Optional

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
USER_ROLES = ["patient", "donor", "hospital", "pharmacy", "admin"]
PRIORITY_LEVELS = ["critical", "urgent", "normal"]

def validate_email(email: str) -> bool:
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(regex, email))

def validate_blood_group(blood_group: str) -> bool:
    return blood_group.upper() in BLOOD_GROUPS

def validate_phone(phone: str) -> bool:
    # Allows standard phone numbers with optional + prefix
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return len(cleaned) >= 8 and len(cleaned) <= 15
