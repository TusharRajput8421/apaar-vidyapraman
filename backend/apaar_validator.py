"""
APAAR Validation & Identity Verification Engine
Implements:
1. Verhoeff Checksum Algorithm (official check-digit standard for 12-digit Aadhaar / APAAR IDs)
2. Format and structural validation (12 numeric digits)
3. Simulated DigiLocker / Academic Bank of Credits (ABC) NAD registry verification
"""

import re
from typing import Tuple, Dict, Any, Optional

# --- Verhoeff Algorithm Tables (Dihedral Group D5) ---
_d_table = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

_p_table = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

_inv_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(num_str: str) -> bool:
    """Validate a numeric string against the Verhoeff checksum algorithm."""
    c = 0
    reversed_str = num_str[::-1]
    for i, char in enumerate(reversed_str):
        if not char.isdigit():
            return False
        c = _d_table[c][_p_table[i % 8][int(char)]]
    return c == 0


def generate_verhoeff_check_digit(num_str: str) -> str:
    """Generate the Verhoeff check digit for an 11-digit or n-digit prefix."""
    c = 0
    reversed_str = num_str[::-1]
    for i, char in enumerate(reversed_str):
        c = _d_table[c][_p_table[(i + 1) % 8][int(char)]]
    return str(_inv_table[c])


def generate_valid_apaar(prefix_11_digits: str) -> str:
    """Helper to generate a valid 12-digit APAAR ID given 11 digits."""
    clean = re.sub(r"\D", "", prefix_11_digits)
    check_digit = generate_verhoeff_check_digit(clean)
    return clean + check_digit


def validate_apaar_structure(apaar_id: str) -> Tuple[bool, str]:
    """
    Validates structural requirements for APAAR ID:
    - 12 numeric digits (ignoring dashes or spaces)
    - Valid Verhoeff check digit
    """
    clean_id = re.sub(r"[\s\-]", "", str(apaar_id or ""))
    
    if len(clean_id) != 12:
        return False, f"APAAR ID must be exactly 12 digits, got {len(clean_id)}"
    
    if not clean_id.isdigit():
        return False, "APAAR ID must contain numeric digits only"
    
    if clean_id[0] in ('0', '1'):
        return False, "APAAR ID cannot start with 0 or 1 (Reserved/Invalid prefix)"
        
    if not validate_verhoeff(clean_id):
        return False, "Invalid APAAR Checksum (Failed Verhoeff check-digit verification)"
        
    return True, "Valid APAAR structure and checksum"


# Simulated DigiLocker / ABC National Registry of APAAR IDs
MOCK_ABC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "987654321012": {
        "full_name": "Aarav Sharma",
        "dob": "2004-05-14",
        "gender": "Male",
        "registered": True,
        "abc_account_id": "ABC-DL-2023-9981"
    },
    "812345678900": {
        "full_name": "Priya Nair",
        "dob": "2003-11-20",
        "gender": "Female",
        "registered": True,
        "abc_account_id": "ABC-MH-2023-4512"
    },
    "734567890125": {
        "full_name": "Rahul Verma",
        "dob": "2004-01-08",
        "gender": "Male",
        "registered": True,
        "abc_account_id": "ABC-KA-2023-7721"
    },
    "654321098763": {
        "full_name": "Ananya Patel",
        "dob": "2004-08-30",
        "gender": "Female",
        "registered": True,
        "abc_account_id": "ABC-GJ-2023-1192"
    },
    "543210987652": {
        "full_name": "Tariq Ahmad Mir",
        "dob": "2003-03-12",
        "gender": "Male",
        "registered": True,
        "abc_account_id": "ABC-JK-2023-0842"
    },
    "918273645018": {
        "full_name": "Vikramaditya Rao",
        "dob": "2003-12-05",
        "gender": "Male",
        "registered": True,
        "abc_account_id": "ABC-MH-2023-5599"
    }
}


def verify_with_abc_registry(apaar_id: str, student_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Simulates querying National Academic Depository (NAD) / Academic Bank of Credits (ABC)
    via DigiLocker API to authenticate student details.
    """
    clean_id = re.sub(r"[\s\-]", "", str(apaar_id or ""))
    
    # 1. Structural Check
    is_valid, msg = validate_apaar_structure(clean_id)
    if not is_valid:
        return {
            "verified": False,
            "status": "CHECKSUM_ERROR",
            "message": msg,
            "apaar_id": clean_id,
            "abc_linked": False
        }
        
    # 2. Query Mock Central Registry
    record = MOCK_ABC_REGISTRY.get(clean_id)
    if not record:
        # For demo purposes, if it passes Verhoeff, auto-generate valid ABC linking
        return {
            "verified": True,
            "status": "VALID_VERHOEFF",
            "message": "Valid APAAR ID (Self-consistent Verhoeff Checksum)",
            "apaar_id": clean_id,
            "abc_linked": True,
            "abc_account_id": f"ABC-NAT-{clean_id[-4:]}"
        }
        
    # 3. Name Match Verification
    if student_name:
        name_lower = student_name.strip().lower()
        rec_name_lower = record["full_name"].strip().lower()
        if name_lower != rec_name_lower and name_lower not in rec_name_lower and rec_name_lower not in name_lower:
            return {
                "verified": False,
                "status": "NAME_MISMATCH",
                "message": f"Name mismatch with ABC Registry: '{student_name}' vs Official '{record['full_name']}'",
                "apaar_id": clean_id,
                "abc_linked": True,
                "official_record": record
            }
            
    return {
        "verified": True,
        "status": "OFFICIALLY_AUTHENTICATED",
        "message": "APAAR ID verified against Ministry of Education ABC/DigiLocker Registry",
        "apaar_id": clean_id,
        "abc_linked": True,
        "official_record": record
    }
