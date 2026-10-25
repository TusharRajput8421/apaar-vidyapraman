"""
Smart India Hackathon Presentation Generator
Generates a pitch deck for Problem Statement 26263:
'Development of an APAAR ID-Based Student Data Management and Verification Platform for AICTE-Approved Institutions'
Using python-pptx with custom styled slides, cards, and professional layout.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "presentation")
OUTPUT_PPTX = os.path.join(OUTPUT_DIR, "VidyaPraman_SIH_Presentation.pptx")

# Color Palette (Deep Government Blue, Tech Teal, Dark Slate, Clean Accent)
COLOR_PRIMARY_DARK = RGBColor(15, 23, 42)      # #0f172a (Slate 900)
COLOR_AICTE_BLUE = RGBColor(30, 58, 138)       # #1e3a8a (Navy Blue)
COLOR_ACCENT_BLUE = RGBColor(37, 99, 235)      # #2563eb (Royal Blue)
COLOR_ACCENT_GOLD = RGBColor(245, 158, 11)     # #f59e0b (Amber/Gold)
COLOR_EMERALD = RGBColor(16, 185, 129)         # #10b981 (Success Green)
COLOR_TEXT_DARK = RGBColor(30, 41, 59)         # #1e293b (Slate 800)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)     # #64748b (Slate 500)
COLOR_CARD_BG = RGBColor(248, 250, 252)        # #f8fafc (Slate 50)
COLOR_CARD_BORDER = RGBColor(226, 232, 240)    # #e2e8f0 (Slate 200)
COLOR_WHITE = RGBColor(255, 255, 255)


def add_header(slide, title_text, category_text="SMART INDIA HACKATHON 2024 | PROBLEM STATEMENT 26263"):
    """Adds a standard header block to content slides."""
    # Category tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = category_text.upper()
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_ACCENT_BLUE

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_AICTE_BLUE


def add_card(slide, left, top, width, height, title, items, badge=None, border_color=COLOR_CARD_BORDER):
    """Draws a card with title, optional badge, and bullet points."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = COLOR_CARD_BG
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.bold = True
    p0.font.size = Pt(14)
    p0.font.color.rgb = COLOR_AICTE_BLUE
    p0.space_after = Pt(8)

    for item in items:
        p = tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_DARK
        p.space_after = Pt(4)


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # ================= SLIDE 1: Title Slide =================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_AICTE_BLUE
    bg1.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2024"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_GOLD
    p.space_after = Pt(10)

    p = tf1.add_paragraph()
    p.text = "VidyaPraman"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "APAAR ID-Based Student Data Management & Verification Platform for AICTE-Approved Institutions"
    p.font.size = Pt(20)
    p.font.color.rgb = RGBColor(219, 234, 254)
    p.space_after = Pt(24)

    p = tf1.add_paragraph()
    p.text = "Problem Statement ID: 26263  |  Ministry: All India Council for Technical Education (AICTE)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(6)

    p = tf1.add_paragraph()
    p.text = "Theme: Smart Education & Regulatory Governance  |  NEP 2020 One Nation One Student ID"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(191, 219, 254)

    # ================= SLIDE 2: Problem Context & Systemic Challenges =================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Current Gaps & Challenges in AICTE Student Data Management")

    add_card(slide2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "1. Lack of Student-Level Records",
             [
                 "Only standalone PGDM institutions currently submit detailed student data.",
                 "10,000+ technical institutions submit aggregate headcounts only during annual approval renewals.",
                 "Zero continuous visibility into actual enrolled students across semesters.",
                 "Difficult to verify whether admitted students exist physically."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "2. Quota & Seat Cap Breaches",
             [
                 "Unmonitored supernumerary admissions violating statutory ceilings.",
                 "NRI Quota capped at 5%, Foreign National (FN/PIO) capped at 15%, TFW at 5%.",
                 "Unscrupulous institutions admit excess students or misclassify seats for capitation fees.",
                 "No real-time intake enforcement engine currently in place."
             ], border_color=COLOR_ACCENT_GOLD)

    add_card(slide2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "3. Concurrent Admissions & Fraud",
             [
                 "Candidates blocking seats in multiple states or institutions simultaneously.",
                 "Drawing multiple government scholarships (PMSSS, Post-Matric) concurrently.",
                 "Ghost students claimed falsely to satisfy Faculty-Student Ratio (FSR) norms.",
                 "Employers face weeks of delays verifying degree certificates manually."
             ], border_color=RGBColor(239, 68, 68))

    # ================= SLIDE 3: Proposed Solution - VidyaPraman Architecture =================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "The Solution: VidyaPraman AICTE-APAAR Ecosystem")

    add_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Unified APAAR-Anchored Architecture",
             [
                 "One Nation, One Student ID (APAAR) serves as the immutable academic anchor under NEP 2020.",
                 "Dual Ingestion Pipeline: Standardized Bulk CSV/Excel batch upload + RESTful Webhook APIs for Campus ERPs (SAP, TCS iON, CollPoll).",
                 "Comprehensive Field Capture: Captures Regular Sanctioned Intake, Supernumerary (TFW, EWS, PMSSS), and International (NRI, OCI, FN, CIWG).",
                 "Central AICTE Repository: Single source of truth for technical education across all states and union territories."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Core Value Proposition & Capabilities",
             [
                 "Automated Intake Enforcement: Rejects or flags admissions exceeding sanctioned capacity in real time.",
                 "Cross-Institutional Deduplication: Immediately detects concurrent full-time admissions across colleges.",
                 "Tamper-Proof Verification: Cryptographic HMAC-SHA256 Signed QR codes for instant offline/online credential verification.",
                 "Accreditation & Governance Reporting: 1-Click generation of verified student datasets for NIRF, NBA, and NAAC."
             ], border_color=COLOR_EMERALD)

    # ================= SLIDE 4: Technical Innovation - Automated Validation Engine =================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Automated Validation & APAAR Identity Verification Engine")

    add_card(slide4, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Verhoeff Checksum Engine",
             [
                 "Official 12-digit check digit algorithm based on the Dihedral Group D5.",
                 "Mathematically catches 100% of single-digit errors and 100% of transposition errors.",
                 "Instant client-side and server-side verification before ledger submission.",
                 "Rejects counterfeit or randomly fabricated student IDs immediately."
             ], border_color=COLOR_ACCENT_BLUE)

    add_card(slide4, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "DigiLocker & ABC Integration",
             [
                 "Simulated integration with Academic Bank of Credits (ABC) & National Academic Depository (NAD).",
                 "Real-time cross-verification of student full name, DOB, and gender against central registry.",
                 "Detects identity theft, proxy admissions, and unauthorized APAAR hijacking.",
                 "Generates automated audit log flags upon name or demographic mismatches."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide4, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Privacy-Preserving Vaults",
             [
                 "Full compliance with the Digital Personal Data Protection (DPDP) Act 2023.",
                 "Zero storage of raw Aadhaar numbers; sensitive demographics de-identified.",
                 "HMAC tokenization prevents unauthorized external correlation.",
                 "Role-Based Access Control (RBAC) ensuring only authorized nodal officers access data."
             ], border_color=COLOR_EMERALD)

    # ================= SLIDE 5: Intelligent Anomaly & Fraud Detection Engine =================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Intelligent Anomaly Detection & Fraud Prevention")

    add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.2),
             "1. Intake Cap & Quota Breach Detector",
             [
                 "Calculates active admissions against Sanctioned Capacity + Statutory Quotas.",
                 "Flags excess admissions instantly: Regular > Sanctioned, NRI > 5%, FN > 15%, TFW > 5%.",
                 "Eliminates illegal over-admissions and fraudulent commercial seat hoarding."
             ], border_color=RGBColor(239, 68, 68))

    add_card(slide5, Inches(0.8), Inches(4.4), Inches(5.6), Inches(2.2),
             "2. Cross-Institution Duplicate Enrolment Detector",
             [
                 "Global indexing across all AICTE-approved institutions in India.",
                 "Instantly alerts AICTE Council if same APAAR is enrolled in 2 colleges concurrently.",
                 "Directly stops dual scholarship fraud and seat blocking syndicates."
             ], border_color=RGBColor(239, 68, 68))

    add_card(slide5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.2),
             "3. Data Inconsistency & Heuristic Checker",
             [
                 "Detects age discrepancies (e.g., student age < 15 or > 60 for regular UG engineering).",
                 "Flags duplicate phone/email clusters indicating agent or paper enrolments.",
                 "Mismatches between state counseling allotment lists and uploaded records."
             ], border_color=COLOR_ACCENT_GOLD)

    add_card(slide5, Inches(6.8), Inches(4.4), Inches(5.6), Inches(2.2),
             "4. Autonomous Regulatory Workflow",
             [
                 "Categorizes violations by severity: CRITICAL, HIGH, MEDIUM.",
                 "Council officers can review violation details and issue instant notices or explanations.",
                 "Immutable resolution notes recorded in compliance audit trails."
             ], border_color=COLOR_AICTE_BLUE)

    # ================= SLIDE 6: Requirement 10 - Printing & Cryptographic QR Verification =================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Verifiable Credentials & Degree Printing Support (Req. 10)")

    add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Degree Printing & Display Support",
             [
                 "Mandatory embedding of APAAR ID + Institutional Student ID on degrees & transcripts.",
                 "Standardized high-security credential template adhering to degree-awarding body guidelines.",
                 "Includes AICTE watermark, institution registration codes, course, batch, and status.",
                 "Enables universities and autonomous colleges to seamlessly print verifiable documents."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Cryptographic Signed QR Verification",
             [
                 "Every credential contains a high-density QR code backed by an HMAC-SHA256 digital signature.",
                 "Employers, background verification agencies, and embassies scan the QR code to verify instantly.",
                 "Displays authoritative status: 'AUTHENTIC & ACTIVE - AICTE REPOSITORY'.",
                 "Zero-Knowledge privacy: Verifies student legitimacy without leaking sensitive phone or address data."
             ], border_color=COLOR_EMERALD)

    # ================= SLIDE 7: Dashboards & Governance Features =================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Dual Dashboards & Data-Driven Governance")

    add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "AICTE National Command Dashboard",
             [
                 "Real-time visibility into all 10,000+ approved institutions across Indian states.",
                 "State-wise intake vs enrolment heatmaps and capacity utilization tracking.",
                 "Live Anomaly Center with one-click audit actions, notice triggers, and explanation workflows.",
                 "Accreditation Data Pipeline: Instant export of verified data for NIRF, NBA, and NAAC."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Institution Nodal Officer Portal",
             [
                 "Interactive live seat matrix gauges showing regular and supernumerary quotas in real time.",
                 "Bulk Ingestion Center: Drag-and-drop CSV upload with instant row-by-row validation feedback.",
                 "Direct Student Registration Form with real-time Verhoeff check-digit verification.",
                 "Student Identity & Certificate Card viewer with one-click print and PDF generation."
             ], border_color=COLOR_ACCENT_BLUE)

    # ================= SLIDE 8: Technology Stack & Security Architecture =================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Technology Stack & Enterprise Security Architecture")

    add_card(slide8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Backend & API Layer",
             [
                 "Python (FastAPI): Ultra-fast asynchronous RESTful microservices.",
                 "Pydantic: Strict schema validation and type-safe data modeling.",
                 "Uvicorn: ASGI high-concurrency web server.",
                 "OpenAPI / Swagger: Standardized API documentation for institutional ERP integration."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Persistence & Crypto",
             [
                 "Relational Ledger: SQLite (prototype) / PostgreSQL with JSONB (production).",
                 "Cryptography Engine: Python hashlib, hmac (SHA-256), and qrcode library.",
                 "Report Generation: reportlab (PDF generation) and xlsxwriter (NIRF compliance).",
                 "Verhoeff Dihedral Group Algorithm for 100% check-digit accuracy."
             ], border_color=COLOR_ACCENT_BLUE)

    add_card(slide8, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Frontend & Security",
             [
                 "Frontend: Responsive Single Page Application (TailwindCSS, Chart.js, Lucide Icons).",
                 "Security: Role-Based Access Control (RBAC), JWT Authentication, TLS encryption.",
                 "DPDP Act 2023: De-identification, consent management, immutable audit logs.",
                 "Zero external build dependencies for maximum reliability."
             ], border_color=COLOR_EMERALD)

    # ================= SLIDE 9: Feasibility, Impact & Business Model =================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "National Impact & Regulatory Feasibility")

    add_card(slide9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Institutional Impact",
             [
                 "Eliminates redundant manual paperwork during annual AICTE approvals.",
                 "Seamless integration with existing college ERPs (SAP, TCS iON, CollPoll).",
                 "Transparent seat matrix prevents accidental over-intake penalties.",
                 "Automated NIRF/NBA accreditation data compilation."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Regulatory Governance",
             [
                 "AICTE gains 100% authentic student-level records across all approved institutions.",
                 "Complete elimination of ghost students and seat-blocking syndicates.",
                 "Prevents leakage of government scholarships and public subsidies.",
                 "Data-driven policy formulation for technical education expansion."
             ], border_color=COLOR_EMERALD)

    add_card(slide9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Student & Employer Value",
             [
                 "Permanent, portable academic identity linked to National Academic Depository (NAD).",
                 "Instant background verification for employers, multinational recruiters, and embassies.",
                 "Zero risk of fraudulent degree claims or fake certificate rackets.",
                 "Complete data privacy protection under DPDP Act 2023."
             ], border_color=COLOR_ACCENT_GOLD)

    # ================= SLIDE 10: Implementation Roadmap & NEP 2020 Vision =================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Implementation Roadmap & Future Vision")

    add_card(slide10, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Phase 1: Hackathon MVP (Current)",
             [
                 "Complete full-stack working platform with AICTE dashboard & college portal.",
                 "Verhoeff APAAR validation & mock DigiLocker/ABC registry.",
                 "Intake cap enforcement & cross-college duplicate detector.",
                 "Signed QR verifiable certificate generation."
             ], border_color=COLOR_EMERALD)

    add_card(slide10, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Phase 2: State Counseling Sync",
             [
                 "API integration with State CET / JEE / CAT counseling authorities.",
                 "Automated reconciliation between allotment lists and actual institutional admissions.",
                 "Integration with National Scholarship Portal (NSP) to prevent duplicate disbursements.",
                 "Pilot testing across 100 benchmark engineering & management colleges."
             ], border_color=COLOR_AICTE_BLUE)

    add_card(slide10, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Phase 3: National Rollout",
             [
                 "Full deployment across all 10,000+ AICTE-approved institutions nationwide.",
                 "Mobile app for student consent management & credential wallet.",
                 "Blockchain-anchored verifiable credentials (W3C standard).",
                 "Complete alignment with NEP 2020 National Education Technology Forum (NETF)."
             ], border_color=COLOR_ACCENT_GOLD)

    # ================= SLIDE 11: Summary & Live Demonstration =================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "VidyaPraman: Live Working Prototype Demonstration")

    add_card(slide11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Live Working Prototype Features",
             [
                 "Live Server Running: http://localhost:8000 with real-time reactive UI.",
                 "Interactive Demo Scenarios:",
                 "  • Authentic Student Verification: APAAR 987654321012 (DTU CSE)",
                 "  • Double Enrolment Detection: APAAR 918273645018 (COEP & BMSCE)",
                 "  • Quota Violation Flag: NRI Quota overflow in BMSCE AI/ML",
                 "  • Checksum Verification: Rejection of invalid APAAR IDs",
                 "Bulk CSV Upload: Drag-and-drop processing with live anomaly detection.",
                 "Official Credential Printing: Verifiable certificate with signed QR code."
             ], border_color=COLOR_EMERALD)

    add_card(slide11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Key Takeaways for AICTE Jury",
             [
                 "Solves All 10 Key Requirements of SIH Problem Statement 26263.",
                 "Goes beyond data collection: Delivers autonomous fraud detection, quota enforcers, and instant verification.",
                 "Production-Ready Architecture: Clean, modular, standards-compliant, and scalable to millions of students.",
                 "Transforms Indian Technical Education into an authentic, verifiable, and transparent national academic ecosystem."
             ], border_color=COLOR_AICTE_BLUE)

    # Save presentation
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prs.save(OUTPUT_PPTX)
    print("SIH Presentation successfully generated at:", OUTPUT_PPTX)


if __name__ == "__main__":
    build_presentation()
