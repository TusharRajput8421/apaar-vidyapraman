# VidyaPraman | AICTE APAAR Student Data Management & Verification Platform
**Smart India Hackathon (SIH) | Problem Statement ID: 26263**  
**Organization:** All India Council for Technical Education (AICTE), Ministry of Education  
**Theme:** Smart Education & Regulatory Governance  

---

## 📌 Executive Summary

Under the National Education Policy (NEP 2020), the **Automated Permanent Academic Account Registry (APAAR ID)** serves as the "One Nation, One Student ID". 

Historically, AICTE received aggregate headcount data from approved institutions during the annual Approval Process Handbook (APH) cycle (except for standalone PGDM institutions). This opened systemic vulnerabilities:
1. **Ghost Students & Paper Enrolments** to falsely satisfy Faculty-Student Ratio (FSR) norms.
2. **Quota Violations** in Supernumerary categories (NRI capped at 5%, FN capped at 15%, TFW capped at 5%).
3. **Concurrent Multi-Institution Enrolments** where a student blocks seats or draws government scholarships across multiple states simultaneously.
4. **Credential Forgery** with no instant cryptographic verification mechanism for employers, embassies, and regulatory councils.

**VidyaPraman** solves this by establishing an end-to-end digital platform where APAAR ID anchors the entire student admission lifecycle, backed by real-time automated validation, intelligent fraud detection, and cryptographic QR credentials.

---

## 🚀 Key Requirements & Technical Implementation Mapping

| Requirement | Platform Capability in VidyaPraman | Implementation Module |
|---|---|---|
| **1. Secure Upload & Update Platform** | Bulk CSV/Excel batch upload & RESTful JSON Webhook APIs for institutional ERPs. | `backend/main.py` (`/api/upload`) |
| **2. Comprehensive Seat Fields** | Captures Sanctioned Regular Intake, Supernumerary (TFW, EWS, PMSSS), and International (NRI, OCI, FN, CIWG). | `backend/database.py` (`sanctioned_intakes`) |
| **3. Automated Validation & Anomalies** | • **Verhoeff Checksum Engine**: Validates 12-digit Dihedral Group $D_5$ check digit.<br>• **Intake Cap Breach**: Flags admissions exceeding regular capacity.<br>• **Quota Ceilings**: Enforces statutory limits (NRI $\le 5\%$, FN $\le 15\%$, TFW $\le 5\%$).<br>• **Cross-Institution Duplicate Detector**: Detects concurrent active admissions. | `backend/apaar_validator.py`<br>`backend/anomaly_detector.py` |
| **4. Real-Time Dashboards** | • **AICTE Council View**: State heatmaps, capacity gauges, real-time anomaly triage feed.<br>• **College View**: Live seat matrix progress bars and bulk drag-and-drop dropzone. | `static/index.html` (Tabs 1 & 2) |
| **5. Secure Verification Mechanism** | Instant verification by scanning cryptographic QR codes or entering APAAR ID. Exposes authentic status without exposing private PII (DPDP Act 2023 compliant). | `backend/verifier_engine.py`<br>`static/index.html` (Tab 3) |
| **6. Verifiable Student Records** | HMAC-SHA256 digital signature embedded into student records linked directly to the AICTE central repository. | `backend/verifier_engine.py` |
| **7. Campus ERP Integration** | Standardized REST API endpoints documented with interactive OpenAPI Swagger UI (`/docs`). | `backend/main.py` |
| **8. Security & Consent Mechanisms** | Role-Based Access Control (RBAC), TLS in transit, AES-256 at rest, encrypted Aadhaar vaults, and immutable audit logs. | `backend/database.py` (`audit_logs`) |
| **9. Policy & NIRF/NBA Reporting** | 1-Click download of verified student datasets in CSV/Excel format for NIRF, NBA, and NAAC accreditation compliance. | `backend/main.py` (`/api/export/nirf`) |
| **10. Degree Printing Support** | High-security official credential template displaying **APAAR ID + Institutional Student Roll ID** alongside a tamper-proof signed QR code. | `backend/verifier_engine.py`<br>`/api/certificate/{apaar_id}` |

---

## 🛠️ Project Directory Structure

```
aicte-apaar-vidyapraman/
├── backend/
│   ├── apaar_validator.py       # Dihedral Group D5 Verhoeff algorithm & Mock ABC/DigiLocker registry
│   ├── anomaly_detector.py      # Intake cap, supernumerary quotas & cross-institution fraud engine
│   ├── database.py              # SQLite relational schema, seed data & immutable audit logs
│   ├── verifier_engine.py       # HMAC-SHA256 signatures, signed QR codes & printable certificate template
│   └── main.py                  # FastAPI REST gateway & static files router
├── static/
│   ├── index.html               # Responsive Single-Page Application (AICTE, College & Verifier Dashboards)
│   ├── login.html               # Multi-Role Government of India / AICTE Authentication Gateway
│   └── sample_aicte_students.csv# Sample CSV for testing bulk upload & anomaly detection
├── data/
│   └── vidyapraman.db           # Pre-seeded SQLite database with institutions and edge-case anomalies
├── presentation/
│   ├── generate_sih_ppt.py      # Automated PowerPoint (.pptx) deck generator using python-pptx
│   ├── VidyaPraman_SIH_Presentation.pptx # 11-Slide Official Pitch Deck for Smart India Hackathon
│   └── VidyaPraman_SIH_Deck.html# Interactive browser-based presentation deck with keyboard controls
├── run_project.bat              # One-click Windows launcher
└── README.md                    # Project documentation
```

---

## 🔐 Multi-Role Authentication & Demo Accounts

Visit the Central Gateway Login at: **[http://localhost:8000/login.html](http://localhost:8000/login.html)**

The login page features **1-Click Jury Quick-Fill Buttons** for effortless testing during hackathon presentations:

| Role Category | Demo User Profile | Login Identifier | Password | Access Capabilities |
|---|---|---|---|---|
| **🏛️ AICTE Central Council** | Dr. Ramesh Unnikrishnan (Advisor) | `admin@aicte.gov.in` | `aicte123` | Full access: National Command Center, live anomaly feed, seat utilization heatmaps, NIRF CSV exports. |
| **🏫 Institution Registrar** | Prof. S. K. Garg (DTU Delhi) | `registrar@dtu.ac.in` | `dtu123` | College-restricted: DTU seat matrix tracker, bulk CSV admissions dropzone, student registration. |
| **🏫 Autonomous Institute** | Dr. D. N. Sonawane (COEP Tech Pune)| `admin@coep.ac.in` | `coep123` | College-restricted: COEP Tech seat matrix and supernumerary quota monitoring. |
| **🔍 Employer / Verifier** | Pooja Deshmukh (Lead Background Check, TCS) | `hr@tcs.com` | `tcs123` | Public/Corporate verification workspace, instant QR code verification. |
| **🎓 Student / Citizen** | Aarav Sharma (DTU CSE Student) | `987654321012` *(APAAR ID)* | *(Direct SSO)* | View personal APAAR passport, ABC credit account (48 credits), manage DPDP employer verification consent. |

---

## ⚡ How to Run & Demo

### 1. Launch the Application Server
Run the one-click batch script or start with Python:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Then open your web browser to: **[http://localhost:8000](http://localhost:8000)**  
Interactive API Docs (Swagger): **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🧪 Demo Test Scenarios for Hackathon Jury

Navigate to **Tab 3 ("Instant Verification & QR")** or click the quick test pills:

| Test Case | APAAR ID | Expected System Behavior |
|---|---|---|
| **1. Authentic Student** | `987654321012` | **VERIFIED & AUTHENTIC**: Aarav Sharma (DTU, CSE). Shows verified cryptographic hash, institutional details, and allows printing the official certificate with QR code. |
| **2. TFW Authentic Student** | `812345678900` | **VERIFIED & AUTHENTIC**: Priya Nair (COEP Tech, CSE - TFW Quota). Validates supernumerary seat allocation. |
| **3. Concurrent Multi-Enrolment Fraud** | `918273645018` | **FLAGGED / SUSPENDED**: Candidate Vikramaditya Rao is actively enrolled in *both* COEP Tech and BMS College of Engineering simultaneously. Blocks verification and logs critical anomaly. |
| **4. Invalid APAAR Checksum** | `309871234560` | **VERIFICATION FAILED**: Rejection due to Verhoeff check-digit calculation mismatch. |
| **5. Bulk Upload Intake & Quota Test** | `static/sample_aicte_students.csv` | Go to **Tab 2 ("Institution Admissions")**, drag and drop the provided `sample_aicte_students.csv`, and run ingestion. The engine immediately admits valid rows and catches invalid check-digits and prefix errors. |

---

## 📽️ Presenting the SIH Pitch Deck

You have two presentation options:
1. **PowerPoint Deck (.pptx):** Open `presentation/VidyaPraman_SIH_Presentation.pptx` in Microsoft PowerPoint or Google Slides.
2. **Interactive Web Presentation Deck (.html):** Open `presentation/VidyaPraman_SIH_Deck.html` in any web browser. Use `Space` or `Right Arrow` to navigate, and click `Fullscreen` for high-impact presentation.
