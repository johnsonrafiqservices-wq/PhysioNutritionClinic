# generate_patient_record_final.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.barcode import code128
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# ---------- Config / Sample Data ----------
OUTPUT = "Elaborated_Patient_Record.pdf"

# Try to register a nicer font
try:
    # Try to use DejaVu Sans if available, or fallback to Helvetica
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    main_font = "DejaVuSans"
except:
    main_font = "Helvetica"

hospital = {
    "name": "ST. RAPHAEL HOSPITAL",
    "address": "123 Health Street, Kampala",
    "tel": "+256 700 123 456",
    "email": "info@straphael.org"
}

patient = {
    "name": "Faith Radio",
    "age": "0",
    "gender": "Male",
    "patient_id": "PT-000001",
    "contact": "+256700535379",
    "email": "prayerpodcast256@gmail.com",
    "address": "No address provided, Entebbe, Central 162",
    "dob": "Sep 12, 2025",
    "blood_type": "Not specified",
    "admission_date": "12 Sept 2025",
    "ward": "Pediatric Ward",
    "bed": "P-05",
    "registered_date": "Sep 12, 2025",
    "last_updated": "-"
}

sections = {
    "Patient Background & Medical History": (
        "Newborn patient delivered at 38 weeks gestation. Apgar scores: 8 at 1 minute, 9 at 5 minutes. "
        "No complications during delivery. Family history: Mother has hypertension, father has asthma. "
        "No known drug allergies. Birth weight: 3.2 kg, length: 50 cm."
    ),
    "Current Presentation / Diagnosis": (
        "Routine newborn assessment. Vital signs within normal limits for age. "
        "Physical examination reveals no abnormalities. Diagnosis: Healthy newborn."
    ),
    "Lab Results": (
        "Blood Pressure: 70/45 mmHg (Normal for age)\n"
        "Heart Rate: 120 bpm (Normal)\n"
        "Respiratory Rate: 40/min (Normal)\n"
        "Temperature: 36.8°C (Normal)\n"
        "Newborn Screening: Pending"
    ),
    "Prescribed Medications": (
        "- Vitamin K 1mg — Single dose administered\n"
        "- Erythromycin ophthalmic ointment — Applied to both eyes\n"
        "- Hepatitis B vaccine — Administered\n"
    ),
    "Treatment Plan & Recommendations": (
        "- Routine newborn care and monitoring\n"
        "- Encourage breastfeeding on demand\n"
        "- Schedule follow-up appointment in 2 weeks\n"
        "- Parent education on newborn care and safety\n"
    ),
    "Doctor's Notes": (
        "Healthy newborn male with normal examination. Parents instructed on cord care, "
        "feeding cues, and danger signs to watch for. Discharge planned for tomorrow if "
        "mother and baby continue to do well."
    )
}

# ---------- Document creation ----------
styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    name="HospitalHeader", 
    fontName=main_font,
    fontSize=18, 
    leading=22, 
    alignment=TA_CENTER,
    textColor=colors.HexColor("#2c5aa0"), 
    spaceAfter=6
))

styles.add(ParagraphStyle(
    name="HospitalInfo", 
    fontName=main_font,
    fontSize=9, 
    leading=11, 
    alignment=TA_CENTER,
    textColor=colors.HexColor("#2c5aa0")
))

styles.add(ParagraphStyle(
    name="PatientName", 
    fontName=f"{main_font}-Bold",
    fontSize=16, 
    leading=18, 
    alignment=TA_LEFT,
    textColor=colors.HexColor("#2c5aa0"),
    spaceAfter=2
))

styles.add(ParagraphStyle(
    name="PatientID", 
    fontName=f"{main_font}-Bold",
    fontSize=14, 
    leading=16, 
    alignment=TA_LEFT,
    textColor=colors.HexColor("#444444"),
    spaceAfter=8
))

styles.add(ParagraphStyle(
    name="PatientInfoLabel", 
    fontName=f"{main_font}-Bold",
    fontSize=10, 
    leading=12,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#444444")
))

styles.add(ParagraphStyle(
    name="PatientInfoValue", 
    fontName=main_font,
    fontSize=10, 
    leading=12,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#666666")
))

styles.add(ParagraphStyle(
    name="SectionTitle", 
    fontName=f"{main_font}-Bold",
    fontSize=12, 
    leading=14, 
    textColor=colors.HexColor("#ffffff"), 
    spaceBefore=8, 
    spaceAfter=4,
    alignment=TA_LEFT,
    backColor=colors.HexColor("#2c5aa0")
))

styles.add(ParagraphStyle(
    name="NormalIndent", 
    fontName=main_font,
    fontSize=10, 
    leading=12,
    alignment=TA_JUSTIFY,
    leftIndent=12
))

styles.add(ParagraphStyle(
    name="Footer", 
    fontName=main_font,
    fontSize=8, 
    leading=10,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#666666")
))

# Override Normal style
styles["Normal"].fontName = main_font
styles["Normal"].fontSize = 10
styles["Normal"].leading = 12
styles["Normal"].alignment = TA_JUSTIFY

doc = SimpleDocTemplate(
    OUTPUT, 
    pagesize=A4,
    topMargin=1.5*cm, 
    bottomMargin=1.5*cm,
    leftMargin=1.5*cm, 
    rightMargin=1.5*cm
)

story = []

# ---------- Header: Logo / Hospital info ----------
# Create a blue header similar to the Faith Radio design
header_bg = Drawing(500, 80)
header_bg.add(Rect(0, 0, 500, 80, strokeColor=colors.HexColor("#2c5aa0"),
              fillColor=colors.HexColor("#2c5aa0"), strokeWidth=0))

# Hospital info paragraph
hospital_header = Paragraph(f"{hospital['name']}", styles["HospitalHeader"])
hospital_info = Paragraph(
    f"{hospital['address']} | Tel: {hospital['tel']} | Email: {hospital['email']}", 
    styles["HospitalInfo"]
)

# Create header table with blue background
header_table = Table(
    [
        [hospital_header],
        [hospital_info]
    ],
    colWidths=[500]
)
header_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
    ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#2c5aa0")),
    ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
]))

story.append(header_table)
story.append(Spacer(1, 15))

# ---------- Patient Information Section ----------
# Patient name and ID in Faith Radio style
story.append(Paragraph(patient["name"], styles["PatientName"]))
story.append(Paragraph(f"<b>{patient['patient_id']}</b>", styles["PatientID"]))

# Patient details in a two-column layout
patient_details_left = [
    ["Date of Birth:", patient["dob"]],
    ["Age:", f"{patient['age']} years"],
    ["Gender:", patient["gender"]],
    ["Blood Type:", patient["blood_type"]]
]

patient_details_right = [
    ["Phone:", patient["contact"]],
    ["Email:", patient["email"]],
    ["Address:", patient["address"]],
    ["Admission Date:", patient["admission_date"]]
]

# Create tables for patient details
left_table = Table(patient_details_left, colWidths=[80, 150])
left_table.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), main_font),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("FONT", (0, 0), (0, -1), f"{main_font}-Bold"),
]))

right_table = Table(patient_details_right, colWidths=[80, 150])
right_table.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), main_font),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("FONT", (0, 0), (0, -1), f"{main_font}-Bold"),
]))

# Combine left and right tables
details_table = Table([[left_table, right_table]], colWidths=[230, 230])
details_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
]))

story.append(details_table)

# Add patient ID again at the bottom of the details section
story.append(Paragraph(f"<b>{patient['patient_id']}</b>", styles["PatientID"]))

# Add registration details
reg_details = [
    ["Registered:", patient["registered_date"]],
    ["Last Updated:", patient["last_updated"]]
]

reg_table = Table(reg_details, colWidths=[80, 150])
reg_table.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), main_font),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("FONT", (0, 0), (0, -1), f"{main_font}-Bold"),
]))

story.append(reg_table)
story.append(Spacer(1, 15))

# Add a separator line
separator = Drawing(500, 1)
separator.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#2c5aa0"), strokeWidth=1))
story.append(separator)
story.append(Spacer(1, 15))

# ---------- Body sections ----------
for title, content in sections.items():
    # Add a colored section header
    story.append(Paragraph(title.upper(), styles["SectionTitle"]))
    
    # Format content with proper line breaks
    safe_content = content.replace("\n", "<br/>")
    
    # Add content with indentation
    story.append(Paragraph(safe_content, styles["NormalIndent"]))
    story.append(Spacer(1, 10))

# ---------- Doctor sign-off ----------
story.append(Spacer(1, 20))

# Create a signature box
signature_data = [
    ["Attending Physician:", "Dr. Grace A. Mugisha"],
    ["Signature:", "____________________________"],
    ["Date:", datetime.now().strftime("%d %b %Y")],
    ["License No:", "MD-2020-12345"]
]

signature_table = Table(signature_data, colWidths=[100, 250])
signature_table.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), main_font),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("FONT", (0, 0), (0, -1), f"{main_font}-Bold"),
]))

story.append(signature_table)

# ---------- Footer ----------
story.append(Spacer(1, 20))
footer = Drawing(500, 20)
footer.add(Line(0, 0, 500, 0, strokeColor=colors.HexColor("#2c5aa0"), strokeWidth=0.5))
story.append(footer)

footer_text = Paragraph(
    f"CONFIDENTIAL MEDICAL RECORD | {hospital['name']} | Generated on: {datetime.now().strftime('%d %b %Y')}", 
    styles["Footer"]
)
story.append(footer_text)

# ---------- Build PDF ----------
doc.build(story)
print(f"PDF generated: {OUTPUT}")