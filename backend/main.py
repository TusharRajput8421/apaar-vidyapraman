"""
FastAPI Application & REST Gateway for VidyaPraman (AICTE APAAR Platform)
Provides endpoints for AICTE Regulatory Monitoring, Institution Admissions,
Bulk Uploads, Anomaly Auditing, Public Verification, and NIRF Export.
"""

import os
import io
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from .database import get_db_connection, log_audit, seed_data
from .apaar_validator import validate_apaar_structure, verify_with_abc_registry
from .anomaly_detector import validate_student_record, process_bulk_batch
from .verifier_engine import verify_student, generate_printable_certificate_html, generate_qr_code_base64

app = FastAPI(
    title="VidyaPraman API - AICTE APAAR Platform",
    description="Unified APAAR-Based Student Data Management, Anomaly Detection & Verification Platform for AICTE-Approved Institutions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


@app.on_event("startup")
def on_startup():
    """Ensure database is seeded on startup."""
    seed_data(force=False)


class LoginPayload(BaseModel):
    identifier: str
    password: Optional[str] = None
    role: Optional[str] = None


class StudentCreatePayload(BaseModel):
    apaar_id: str
    student_roll_no: str
    aicte_id: str
    course_code: str
    academic_year: str = "2024-25"
    full_name: str
    gender: str = "Male"
    dob: str = "2004-01-01"
    category: str = "Regular"
    admission_mode: str = "Central Counseling"


class AnomalyResolvePayload(BaseModel):
    status: str = "RESOLVED"
    resolution_notes: str


# --- Authentication & RBAC Endpoints ---

@app.post("/api/auth/login")
def login_user(payload: LoginPayload):
    """
    Role-Based Authentication Gateway for AICTE Council, Institution Nodal Officers,
    Employers/Verifiers, and Students (via APAAR ID).
    """
    import hashlib
    conn = get_db_connection()
    cursor = conn.cursor()

    ident = payload.identifier.strip()
    role_hint = (payload.role or "").upper()

    # 1. Student Login via 12-digit APAAR ID
    clean_apaar = ident.replace("-", "").replace(" ", "")
    if role_hint == "STUDENT" or (clean_apaar.isdigit() and len(clean_apaar) == 12):
        cursor.execute("""
            SELECT s.*, i.name as institution_name
            FROM students s
            JOIN institutions i ON s.aicte_id = i.aicte_id
            WHERE s.apaar_id = ?
        """, (clean_apaar,))
        student = cursor.fetchone()
        
        if student:
            log_audit("STUDENT", "PORTAL_LOGIN", f"Student {student['full_name']} logged in via APAAR {clean_apaar}")
            conn.close()
            return {
                "success": True,
                "role": "STUDENT",
                "user": {
                    "user_id": f"STU-{clean_apaar[-4:]}",
                    "full_name": student["full_name"],
                    "email": f"{student['full_name'].lower().replace(' ', '.')}@edu.in",
                    "role": "STUDENT",
                    "apaar_id": clean_apaar,
                    "aicte_id": student["aicte_id"],
                    "institution_name": student["institution_name"],
                    "designation": f"Enrolled Student ({student['course_code']})",
                    "token": f"TOKEN-STU-{clean_apaar[-6:]}"
                }
            }

    # 2. Staff / Council / Verifier Login via Email + Password
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (ident,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="User account not found. Please check credentials or select a demo role.")

    pwd_hash = hashlib.sha256((payload.password or "").encode("utf-8")).hexdigest()
    if user["password_hash"] != pwd_hash:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid password. Please check your credentials.")

    inst_name = None
    if user["aicte_id"]:
        cursor.execute("SELECT name FROM institutions WHERE aicte_id = ?", (user["aicte_id"],))
        inst_row = cursor.fetchone()
        if inst_row:
            inst_name = inst_row["name"]

    conn.close()

    log_audit(user["role"], "PORTAL_LOGIN", f"User {user['full_name']} ({user['email']}) authenticated successfully.")

    return {
        "success": True,
        "role": user["role"],
        "user": {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "aicte_id": user["aicte_id"],
            "institution_name": inst_name,
            "apaar_id": user["apaar_id"],
            "designation": user["designation"],
            "token": f"TOKEN-AUTH-{user['user_id']}"
        }
    }


@app.get("/api/student/profile/{apaar_id}")
def get_student_profile(apaar_id: str):
    """Personalized DigiLocker / APAAR Academic Card & Consent Management."""
    clean_id = apaar_id.strip().replace("-", "").replace(" ", "")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, i.name as institution_name, i.state, i.city,
               si.course_name, si.degree_level
        FROM students s
        JOIN institutions i ON s.aicte_id = i.aicte_id
        LEFT JOIN sanctioned_intakes si ON s.aicte_id = si.aicte_id AND s.course_code = si.course_code
        WHERE s.apaar_id = ?
    """, (clean_id,))
    student = cursor.fetchone()
    conn.close()

    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")

    qr_b64 = generate_qr_code_base64(
        student["apaar_id"], student["aicte_id"], student["course_code"], student["student_roll_no"]
    )

    return {
        "student": dict(student),
        "qr_code": qr_b64,
        "abc_account_id": f"ABC-NAT-{clean_id[-4:]}",
        "abc_credits_accumulated": 48,
        "verification_consent_active": True,
        "dpdp_status": "DATA_MINIMIZATION_ENABLED"
    }


# --- AICTE Regulatory Dashboard Endpoints ---

@app.get("/api/stats")
def get_national_stats():
    """Returns aggregated high-level KPIs for AICTE Central Command."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM institutions")
    total_institutions = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(regular_intake) FROM sanctioned_intakes")
    total_sanctioned_intake = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'ACTIVE'")
    total_enrolled = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomaly_flags WHERE status = 'OPEN'")
    open_anomalies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM anomaly_flags WHERE status = 'OPEN' AND severity = 'CRITICAL'")
    critical_anomalies = cursor.fetchone()[0]

    # Category distribution
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM students
        GROUP BY category
    """)
    category_distribution = {row["category"]: row["count"] for row in cursor.fetchall()}

    # State distribution
    cursor.execute("""
        SELECT i.state, COUNT(DISTINCT i.aicte_id) as institutions_count,
               COUNT(s.apaar_id) as enrolled_count
        FROM institutions i
        LEFT JOIN students s ON i.aicte_id = s.aicte_id
        GROUP BY i.state
    """)
    state_stats = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_institutions": total_institutions,
        "total_sanctioned_intake": total_sanctioned_intake,
        "total_enrolled": total_enrolled,
        "enrolment_ratio": round((total_enrolled / max(total_sanctioned_intake, 1)) * 100, 2),
        "open_anomalies": open_anomalies,
        "critical_anomalies": critical_anomalies,
        "category_distribution": category_distribution,
        "state_stats": state_stats,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/institutions")
def list_institutions():
    """Lists all approved institutions with intake and current student counts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, 
               COALESCE(SUM(si.regular_intake), 0) as total_sanctioned,
               COALESCE(sc.enrolled_count, 0) as total_enrolled,
               COALESCE(ac.anomaly_count, 0) as anomaly_count
        FROM institutions i
        LEFT JOIN sanctioned_intakes si ON i.aicte_id = si.aicte_id
        LEFT JOIN (
            SELECT aicte_id, COUNT(*) as enrolled_count
            FROM students WHERE status = 'ACTIVE'
            GROUP BY aicte_id
        ) sc ON i.aicte_id = sc.aicte_id
        LEFT JOIN (
            SELECT aicte_id, COUNT(*) as anomaly_count
            FROM anomaly_flags WHERE status = 'OPEN'
            GROUP BY aicte_id
        ) ac ON i.aicte_id = ac.aicte_id
        GROUP BY i.aicte_id
    """)
    institutions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return institutions


@app.get("/api/institutions/{aicte_id}")
def get_institution_seat_matrix(aicte_id: str):
    """Detailed seat matrix breakdown for a specific institution."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM institutions WHERE aicte_id = ?", (aicte_id,))
    inst = cursor.fetchone()
    if not inst:
        conn.close()
        raise HTTPException(status_code=404, detail="Institution not found")

    cursor.execute("""
        SELECT si.*, 
               COALESCE(COUNT(s.apaar_id), 0) as enrolled_count
        FROM sanctioned_intakes si
        LEFT JOIN students s ON si.aicte_id = s.aicte_id AND si.course_code = s.course_code AND s.status = 'ACTIVE'
        WHERE si.aicte_id = ?
        GROUP BY si.id
    """, (aicte_id,))
    courses = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "institution": dict(inst),
        "seat_matrix": courses
    }


# --- Student Management & Bulk Ingestion Endpoints ---

@app.get("/api/students")
def list_students(
    aicte_id: Optional[str] = None,
    course_code: Optional[str] = None,
    search: Optional[str] = None
):
    """Lists students filtered by institution, course, or APAAR/name search."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.*, i.name as institution_name
        FROM students s
        JOIN institutions i ON s.aicte_id = i.aicte_id
        WHERE 1=1
    """
    params = []

    if aicte_id:
        query += " AND s.aicte_id = ?"
        params.append(aicte_id)
    if course_code:
        query += " AND s.course_code = ?"
        params.append(course_code)
    if search:
        query += " AND (s.apaar_id LIKE ? OR s.full_name LIKE ? OR s.student_roll_no LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY s.created_at DESC LIMIT 100"
    cursor.execute(query, params)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students


@app.post("/api/student/create")
def create_single_student(payload: StudentCreatePayload):
    """Single student registration with immediate automated validation."""
    data = payload.dict()
    is_valid, anomalies, enriched = validate_student_record(data)

    conn = get_db_connection()
    cursor = conn.cursor()

    for a in anomalies:
        cursor.execute("""
            INSERT OR REPLACE INTO anomaly_flags (flag_id, apaar_id, aicte_id, anomaly_type, severity, description, detected_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            a["flag_id"], a["apaar_id"], a["aicte_id"], a["anomaly_type"],
            a["severity"], a["description"], a["detected_at"], a["status"]
        ))

    has_critical = any(a["severity"] == "CRITICAL" for a in anomalies)
    if not has_critical:
        cursor.execute("""
            INSERT OR REPLACE INTO students (
                apaar_id, student_roll_no, aicte_id, course_code, academic_year,
                full_name, gender, dob, category, admission_date, admission_mode,
                status, digital_signature, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            enriched["apaar_id"], enriched["student_roll_no"], enriched["aicte_id"],
            enriched["course_code"], enriched["academic_year"], enriched["full_name"],
            enriched["gender"], enriched["dob"], enriched["category"],
            enriched["admission_date"], enriched["admission_mode"], enriched["status"],
            enriched["digital_signature"], enriched["created_at"]
        ))

    conn.commit()
    conn.close()

    log_audit("INSTITUTION_ADMIN", "STUDENT_REGISTERED", f"Processed APAAR: {data['apaar_id']} for {data['aicte_id']}")

    return {
        "success": not has_critical,
        "is_valid": is_valid,
        "student": enriched,
        "anomalies": anomalies
    }


@app.post("/api/upload")
async def bulk_upload_students(
    aicte_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Handles bulk CSV ingestion from institutions with instant validation."""
    content = await file.read()
    text = content.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))

    records = []
    for row in reader:
        records.append({
            "apaar_id": row.get("apaar_id") or row.get("APAAR_ID", ""),
            "student_roll_no": row.get("student_roll_no") or row.get("Roll_No", ""),
            "course_code": row.get("course_code") or row.get("Course_Code", "CSE"),
            "full_name": row.get("full_name") or row.get("Student_Name", ""),
            "gender": row.get("gender") or row.get("Gender", "Male"),
            "dob": row.get("dob") or row.get("DOB", "2004-01-01"),
            "category": row.get("category") or row.get("Category", "Regular"),
            "admission_mode": row.get("admission_mode") or row.get("Admission_Mode", "Central Counseling"),
            "academic_year": row.get("academic_year") or "2024-25"
        })

    result = process_bulk_batch(records, aicte_id, persist_clean=True)
    log_audit(
        "INSTITUTION_REGISTRAR",
        "BULK_CSV_UPLOAD",
        f"College {aicte_id} uploaded {len(records)} records. Enrolled: {result['successfully_enrolled']}, Anomalies: {result['anomalies_detected']}"
    )

    return result


# --- Anomaly Auditing Endpoints ---

@app.get("/api/anomalies")
def list_anomalies(
    severity: Optional[str] = None,
    status: Optional[str] = "OPEN",
    aicte_id: Optional[str] = None
):
    """Lists detected anomalies with filters for council audit review."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.*, i.name as institution_name
        FROM anomaly_flags a
        JOIN institutions i ON a.aicte_id = i.aicte_id
        WHERE 1=1
    """
    params = []

    if status and status != "ALL":
        query += " AND a.status = ?"
        params.append(status)
    if severity and severity != "ALL":
        query += " AND a.severity = ?"
        params.append(severity)
    if aicte_id:
        query += " AND a.aicte_id = ?"
        params.append(aicte_id)

    query += " ORDER BY a.detected_at DESC"
    cursor.execute(query, params)
    anomalies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return anomalies


@app.post("/api/anomalies/{flag_id}/resolve")
def resolve_anomaly(flag_id: str, payload: AnomalyResolvePayload):
    """Council action: resolves or dismisses an anomaly flag with explanation."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE anomaly_flags
        SET status = ?, resolution_notes = ?
        WHERE flag_id = ?
    """, (payload.status, payload.resolution_notes, flag_id))
    conn.commit()
    conn.close()

    log_audit("AICTE_AUDIT_OFFICER", "ANOMALY_RESOLVED", f"Flag {flag_id} resolved with notes: {payload.resolution_notes}")

    return {"success": True, "flag_id": flag_id, "status": payload.status}


# --- Public / Employer Verification Endpoints ---

@app.get("/api/verify")
def public_verify_student(apaar: str, sig: Optional[str] = None):
    """Instant public / employer verification lookup."""
    res = verify_student(apaar, input_signature=sig)
    log_audit("PUBLIC_VERIFIER", "STUDENT_VERIFICATION", f"Queried APAAR: {apaar}, Verified: {res['verified']}")
    return res


@app.get("/api/certificate/{apaar_id}", response_class=HTMLResponse)
def get_printable_certificate(apaar_id: str):
    """Requirement 10: Renders official printable certificate with APAAR + Student ID."""
    html = generate_printable_certificate_html(apaar_id)
    if not html:
        raise HTTPException(status_code=404, detail="Student credential not found or not verifiable.")
    return HTMLResponse(content=html)


# --- NIRF & Accreditation Data Export ---

@app.get("/api/export/nirf")
def export_nirf_compliance_csv():
    """Generates a verified, real-time CSV report for NIRF/NBA accreditation."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.aicte_id, i.name as institution_name, i.state, si.course_code, si.course_name,
               si.degree_level, si.regular_intake,
               COUNT(s.apaar_id) as actual_enrolment,
               SUM(CASE WHEN s.category = 'TFW' THEN 1 ELSE 0 END) as tfw_students,
               SUM(CASE WHEN s.category = 'EWS' THEN 1 ELSE 0 END) as ews_students,
               SUM(CASE WHEN s.category = 'NRI' THEN 1 ELSE 0 END) as nri_students,
               SUM(CASE WHEN s.category IN ('FN', 'OCI') THEN 1 ELSE 0 END) as international_students
        FROM institutions i
        JOIN sanctioned_intakes si ON i.aicte_id = si.aicte_id
        LEFT JOIN students s ON si.aicte_id = s.aicte_id AND si.course_code = s.course_code AND s.status = 'ACTIVE'
        GROUP BY i.aicte_id, si.course_code
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "AICTE_Permanent_ID", "Institution_Name", "State", "Course_Code", "Course_Name",
        "Degree_Level", "Sanctioned_Intake", "Actual_Enrolment", "TFW_Admissions",
        "EWS_Admissions", "NRI_Admissions", "International_Admissions", "Data_Authenticity"
    ])

    for r in rows:
        writer.writerow([
            r["aicte_id"], r["institution_name"], r["state"], r["course_code"], r["course_name"],
            r["degree_level"], r["regular_intake"], r["actual_enrolment"], r["tfw_students"],
            r["ews_students"], r["nri_students"], r["international_students"], "APAAR-VERIFIED"
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=AICTE_APAAR_NIRF_Compliance_Report.csv"}
    )


@app.get("/api/logs")
def get_audit_trail():
    """Returns immutable audit logs per DPDP Act 2023 regulations."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50")
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs


# Mount static directory for frontend
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
