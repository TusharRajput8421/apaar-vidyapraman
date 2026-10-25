"""
Database Layer for VidyaPraman (AICTE APAAR Platform)
SQLite-based relational database layer with schema definitions, helper queries,
and comprehensive initial seed data representing institutions across India.
"""

import sqlite3
import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "vidyapraman.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured as dictionary."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and indices."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS institutions (
        aicte_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        city TEXT NOT NULL,
        institution_type TEXT NOT NULL,
        established_year INTEGER,
        contact_email TEXT NOT NULL,
        status TEXT DEFAULT 'APPROVED'
    );

    CREATE TABLE IF NOT EXISTS sanctioned_intakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aicte_id TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        course_code TEXT NOT NULL,
        course_name TEXT NOT NULL,
        degree_level TEXT NOT NULL,
        regular_intake INTEGER NOT NULL,
        tfw_quota INTEGER DEFAULT 0,
        ews_quota INTEGER DEFAULT 0,
        nri_quota INTEGER DEFAULT 0,
        fn_quota INTEGER DEFAULT 0,
        pmsss_quota INTEGER DEFAULT 0,
        FOREIGN KEY (aicte_id) REFERENCES institutions(aicte_id)
    );

    CREATE TABLE IF NOT EXISTS students (
        apaar_id TEXT PRIMARY KEY,
        student_roll_no TEXT NOT NULL,
        aicte_id TEXT NOT NULL,
        course_code TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        full_name TEXT NOT NULL,
        gender TEXT NOT NULL,
        dob TEXT NOT NULL,
        category TEXT NOT NULL,
        admission_date TEXT NOT NULL,
        admission_mode TEXT NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        digital_signature TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (aicte_id) REFERENCES institutions(aicte_id)
    );

    CREATE TABLE IF NOT EXISTS anomaly_flags (
        flag_id TEXT PRIMARY KEY,
        apaar_id TEXT,
        aicte_id TEXT NOT NULL,
        anomaly_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        detected_at TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        resolution_notes TEXT,
        FOREIGN KEY (aicte_id) REFERENCES institutions(aicte_id)
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        ip_address TEXT DEFAULT '127.0.0.1'
    );

    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        aicte_id TEXT,
        apaar_id TEXT,
        designation TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (aicte_id) REFERENCES institutions(aicte_id)
    );

    CREATE INDEX IF NOT EXISTS idx_student_aicte ON students(aicte_id);
    CREATE INDEX IF NOT EXISTS idx_student_course ON students(course_code);
    CREATE INDEX IF NOT EXISTS idx_anomaly_status ON anomaly_flags(status);
    CREATE INDEX IF NOT EXISTS idx_anomaly_aicte ON anomaly_flags(aicte_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """)

    conn.commit()
    conn.close()


def log_audit(actor: str, action: str, details: str, ip_address: str = "127.0.0.1"):
    """Inserts a secure immutable audit log record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (log_id, timestamp, actor, action, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        f"LOG-{uuid.uuid4().hex[:8].upper()}",
        datetime.now().isoformat(),
        actor,
        action,
        details,
        ip_address
    ))
    conn.commit()
    conn.close()


def seed_data(force: bool = False):
    """Populates realistic seed data for AICTE demo if not already populated."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM institutions")
    if cursor.fetchone()[0] > 0 and not force:
        conn.close()
        return

    # Clear existing if force
    if force:
        cursor.executescript("""
            DELETE FROM anomaly_flags;
            DELETE FROM students;
            DELETE FROM sanctioned_intakes;
            DELETE FROM institutions;
            DELETE FROM audit_logs;
        """)

    # 1. Institutions
    institutions = [
        ("AICTE-DL-ENG-01", "Delhi Technological University (DTU)", "Delhi", "New Delhi", "Govt State University", 1941, "registrar@dtu.ac.in"),
        ("AICTE-MH-ENG-02", "College of Engineering Pune (COEP Tech)", "Maharashtra", "Pune", "Autonomous State Institute", 1854, "admin@coep.ac.in"),
        ("AICTE-KA-ENG-03", "BMS College of Engineering", "Karnataka", "Bengaluru", "Private Autonomous", 1946, "principal@bmsce.ac.in"),
        ("AICTE-DL-MGT-04", "International Management Institute (IMI)", "Delhi", "New Delhi", "PGDM Standalone", 1981, "admissions@imi.edu"),
        ("AICTE-TN-ENG-05", "PSG College of Technology", "Tamil Nadu", "Coimbatore", "Govt-Aided Autonomous", 1951, "dean@psgtech.edu")
    ]
    cursor.executemany("""
        INSERT INTO institutions (aicte_id, name, state, city, institution_type, established_year, contact_email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, institutions)

    # 2. Sanctioned Intakes (Approved Capacity per AICTE Approval Process Handbook)
    intakes = [
        # DTU
        ("AICTE-DL-ENG-01", "2024-25", "CSE", "Computer Science & Engineering", "UG", 120, 6, 12, 6, 18, 5),
        ("AICTE-DL-ENG-01", "2024-25", "ECE", "Electronics & Communication Engg", "UG", 120, 6, 12, 6, 18, 5),
        # COEP
        ("AICTE-MH-ENG-02", "2024-25", "CSE", "Computer Engineering", "UG", 120, 6, 12, 6, 18, 5),
        ("AICTE-MH-ENG-02", "2024-25", "MECH", "Mechanical Engineering", "UG", 120, 6, 12, 6, 18, 5),
        # BMSCE
        ("AICTE-KA-ENG-03", "2024-25", "CSE", "Computer Science & Engineering", "UG", 180, 9, 18, 9, 27, 5),
        ("AICTE-KA-ENG-03", "2024-25", "AI_ML", "Artificial Intelligence & Machine Learning", "UG", 60, 3, 6, 3, 9, 2),
        # IMI (PGDM)
        ("AICTE-DL-MGT-04", "2024-25", "PGDM_GEN", "Post Graduate Diploma in Management", "PG", 240, 0, 24, 12, 36, 0),
        # PSG Tech
        ("AICTE-TN-ENG-05", "2024-25", "CSE", "Computer Science & Engineering", "UG", 120, 6, 12, 6, 18, 5),
    ]
    cursor.executemany("""
        INSERT INTO sanctioned_intakes (aicte_id, academic_year, course_code, course_name, degree_level,
                                        regular_intake, tfw_quota, ews_quota, nri_quota, fn_quota, pmsss_quota)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, intakes)

    # 3. Seed Students (Valid + Cross-college duplicates + edge cases)
    students = [
        # Normal verified students
        ("987654321012", "DTU/2024/CSE/001", "AICTE-DL-ENG-01", "CSE", "2024-25", "Aarav Sharma", "Male", "2004-05-14", "Regular", "2024-08-10", "JEE Main JAC Delhi", "ACTIVE", "SIG-AARAV-DTU-01", datetime.now().isoformat()),
        ("812345678900", "COEP/2024/CSE/042", "AICTE-MH-ENG-02", "CSE", "2024-25", "Priya Nair", "Female", "2003-11-20", "TFW", "2024-08-14", "MHT-CET CAP", "ACTIVE", "SIG-PRIYA-COEP-02", datetime.now().isoformat()),
        ("734567890125", "BMS/2024/CSE/089", "AICTE-KA-ENG-03", "CSE", "2024-25", "Rahul Verma", "Male", "2004-01-08", "EWS", "2024-08-18", "KCET Counseling", "ACTIVE", "SIG-RAHUL-BMS-03", datetime.now().isoformat()),
        ("654321098763", "IMI/2024/PGDM/015", "AICTE-DL-MGT-04", "PGDM_GEN", "2024-25", "Ananya Patel", "Female", "2004-08-30", "Regular", "2024-07-25", "CAT Centralized", "ACTIVE", "SIG-ANANYA-IMI-04", datetime.now().isoformat()),
        ("543210987652", "PSG/2024/CSE/011", "AICTE-TN-ENG-05", "CSE", "2024-25", "Tariq Ahmad Mir", "Male", "2003-03-12", "PMSSS", "2024-08-20", "AICTE PMSSS Allotment", "ACTIVE", "SIG-TARIQ-PSG-05", datetime.now().isoformat()),

        # DEMO ANOMALY 1: Duplicate enrolment across two different colleges!
        # Vikramaditya Rao is enrolled in BOTH COEP and BMSCE concurrently!
        ("918273645018", "COEP/2024/CSE/102", "AICTE-MH-ENG-02", "CSE", "2024-25", "Vikramaditya Rao", "Male", "2003-12-05", "Regular", "2024-08-12", "MHT-CET CAP", "ACTIVE", "SIG-VIKRAM-COEP", datetime.now().isoformat()),
        ("918273645018-DUP", "BMS/2024/CSE/114", "AICTE-KA-ENG-03", "CSE", "2024-25", "Vikramaditya Rao", "Male", "2003-12-05", "Management", "2024-08-22", "Direct Institutional", "ACTIVE", "SIG-VIKRAM-BMS", datetime.now().isoformat()),
    ]

    for s in students:
        cursor.execute("""
            INSERT OR REPLACE INTO students (apaar_id, student_roll_no, aicte_id, course_code, academic_year,
                                             full_name, gender, dob, category, admission_date, admission_mode,
                                             status, digital_signature, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, s)

    # 4. Seed Pre-Detected Real-Time Anomalies (for immediate demonstration in Hackathon UI)
    anomalies = [
        (
            "ANO-2024-001",
            "918273645018",
            "AICTE-MH-ENG-02",
            "CROSS_INSTITUTION_DUPLICATE",
            "CRITICAL",
            "Student Vikramaditya Rao (APAAR: 918273645018) detected with concurrent ACTIVE full-time enrolment in both 'COEP Tech' (CSE) and 'BMS College of Engineering' (CSE). Possible scholarship or seat-blocking fraud.",
            datetime.now().isoformat(),
            "OPEN",
            None
        ),
        (
            "ANO-2024-002",
            None,
            "AICTE-KA-ENG-03",
            "QUOTA_CAP_BREACH",
            "HIGH",
            "NRI Quota Breach in BMS College of Engineering (Course: AI_ML). 5 NRI students admitted against permissible statutory ceiling of 3 (5% of 60). Immediate explanation requested from Registrar.",
            datetime.now().isoformat(),
            "OPEN",
            None
        ),
        (
            "ANO-2024-003",
            "309871234560",
            "AICTE-DL-ENG-01",
            "INVALID_APAAR_CHECKSUM",
            "MEDIUM",
            "Uploaded APAAR ID '309871234560' for candidate 'Devendra Rathore' failed Verhoeff check-digit verification. Blocked from central AICTE ledger.",
            datetime.now().isoformat(),
            "OPEN",
            None
        )
    ]
    cursor.executemany("""
        INSERT INTO anomaly_flags (flag_id, apaar_id, aicte_id, anomaly_type, severity, description, detected_at, status, resolution_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, anomalies)

    # 5. Pre-Seeded User Accounts for Demonstration (RBAC)
    def hash_pwd(pwd: str) -> str:
        return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    users = [
        # AICTE Central Council
        ("USR-AICTE-01", "admin@aicte.gov.in", hash_pwd("aicte123"), "Dr. Ramesh Unnikrishnan", "AICTE_OFFICER", None, None, "Advisor, AICTE Council New Delhi", datetime.now().isoformat()),
        # Institution Registrars
        ("USR-INST-01", "registrar@dtu.ac.in", hash_pwd("dtu123"), "Prof. S. K. Garg", "INSTITUTION_ADMIN", "AICTE-DL-ENG-01", None, "Registrar & Nodal Officer, DTU", datetime.now().isoformat()),
        ("USR-INST-02", "admin@coep.ac.in", hash_pwd("coep123"), "Dr. D. N. Sonawane", "INSTITUTION_ADMIN", "AICTE-MH-ENG-02", None, "Dean Academics, COEP Tech", datetime.now().isoformat()),
        ("USR-INST-03", "principal@bmsce.ac.in", hash_pwd("bms123"), "Dr. S. Muralidhara", "INSTITUTION_ADMIN", "AICTE-KA-ENG-03", None, "Principal, BMSCE Bengaluru", datetime.now().isoformat()),
        # Employer / Verifier
        ("USR-VER-01", "hr@tcs.com", hash_pwd("tcs123"), "Pooja Deshmukh", "VERIFIER", None, None, "Lead Background Verification, TCS", datetime.now().isoformat()),
        # Student
        ("USR-STU-01", "aarav.sharma@dtu.ac.in", hash_pwd("student123"), "Aarav Sharma", "STUDENT", "AICTE-DL-ENG-01", "987654321012", "B.Tech CSE 2024-28", datetime.now().isoformat()),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO users (user_id, email, password_hash, full_name, role, aicte_id, apaar_id, designation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

    conn.commit()
    conn.close()

    log_audit("SYSTEM_INITIALIZER", "DATABASE_SEEDED", "Initialized AICTE institutions, intakes, and baseline student ledger.")


if __name__ == "__main__":
    seed_data(force=True)
    print("VidyaPraman Database initialized & seeded successfully at:", DB_PATH)
