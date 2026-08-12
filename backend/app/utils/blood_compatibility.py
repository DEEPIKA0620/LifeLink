from typing import List, Dict

# ABO and Rh blood group compatibility matrix
# Key: Recipient blood group -> Value: List of donor blood groups compatible
COMPATIBILITY_MATRIX: Dict[str, List[str]] = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"] # Universal recipient
}

def is_blood_compatible(recipient_group: str, donor_group: str) -> bool:
    """
    Checks if a donor's blood group is medically compatible with a recipient's blood group.
    """
    recipient_group = recipient_group.strip().upper()
    donor_group = donor_group.strip().upper()
    
    compatible_donors = COMPATIBILITY_MATRIX.get(recipient_group, [])
    return donor_group in compatible_donors

def get_compatible_donor_groups(recipient_group: str) -> List[str]:
    """
    Returns list of donor blood groups compatible with the given recipient blood group.
    """
    recipient_group = recipient_group.strip().upper()
    return COMPATIBILITY_MATRIX.get(recipient_group, [])
