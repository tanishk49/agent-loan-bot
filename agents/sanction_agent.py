from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import lightgrey
from datetime import date
import os
import uuid
from textwrap import wrap

OUTPUT_DIR = "sanction_letters"


def generate_sanction(customer_name, loan_amount, interest_rate):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    today = date.today().strftime("%d-%m-%Y")
    tenure_months = 36
    loan_id = f"TCPL-{uuid.uuid4().hex[:8].upper()}"

    emi = int((loan_amount * (1 + (interest_rate / 100))) / tenure_months)

    file_path = os.path.join(
        OUTPUT_DIR,
        f"Loan_Sanction_{loan_id}.pdf"
    )

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # ================= CONSTANT MARGINS =================
    LEFT = 2 * cm
    RIGHT = width - 2 * cm
    TOP = height - 2.2 * cm
    BOTTOM = 2 * cm

    # ================= PAGE BORDER =================
    c.setLineWidth(1)
    c.rect(1.2 * cm, 1.2 * cm, width - 2.4 * cm, height - 2.4 * cm)

    # ================= WATERMARK =================
    c.saveState()
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(lightgrey)
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "TATA CAPITAL")
    c.restoreState()

    # ================= HEADER =================
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, TOP, "TATA CAPITAL (Demo)")

    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(
        width / 2,
        TOP - 1 * cm,
        "PERSONAL LOAN SANCTION LETTER"
    )

    c.line(LEFT, TOP - 1.4 * cm, RIGHT, TOP - 1.4 * cm)

    # ================= META INFO =================
    c.setFont("Helvetica", 10)
    c.drawString(LEFT, TOP - 2.3 * cm, f"Loan ID: {loan_id}")
    c.drawRightString(RIGHT, TOP - 2.3 * cm, f"Date: {today}")

    # ================= INTRO =================
    y = TOP - 3.8 * cm
    c.setFont("Helvetica", 11)

    c.drawString(LEFT, y, f"Dear {customer_name},")
    y -= 0.8 * cm

    intro_text = (
        "We are pleased to inform you that your Personal Loan application "
        "has been approved based on our internal credit and risk assessment."
    )

    for line in wrap(intro_text, 90):
        c.drawString(LEFT, y, line)
        y -= 0.6 * cm

    y -= 0.4 * cm
    c.drawString(LEFT, y, "The details of the sanctioned loan are outlined below:")

    # ================= LOAN DETAILS BOX =================
    box_top = y - 1.5 * cm
    box_height = 5 * cm
    box_width = RIGHT - LEFT

    c.rect(LEFT, box_top - box_height, box_width, box_height)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT + 0.5 * cm, box_top - 0.9 * cm, "Loan Details")

    c.setFont("Helvetica", 11)
    y2 = box_top - 2 * cm
    gap = 0.85 * cm

    c.drawString(LEFT + 0.5 * cm, y2, f"Sanctioned Loan Amount : INR {loan_amount:,}")
    y2 -= gap
    c.drawString(LEFT + 0.5 * cm, y2, f"Interest Rate           : {interest_rate}% per annum")
    y2 -= gap
    c.drawString(LEFT + 0.5 * cm, y2, f"Loan Tenure             : {tenure_months} months")
    y2 -= gap
    c.drawString(LEFT + 0.5 * cm, y2, f"Monthly EMI             : INR {emi:,}")

    # ================= DISCLAIMER =================
    y = box_top - box_height - 1.2 * cm
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(LEFT, y, "Disclaimer:")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10.2)
    disclaimer = (
        "This sanction letter is issued subject to verification of documents, "
        "completion of all mandatory formalities, and adherence to the terms "
        "and conditions of Tata Capital. The final loan disbursement is at the "
        "sole discretion of Tata Capital and may be modified or withdrawn "
        "without prior notice in case of material discrepancies."
    )

    for line in wrap(disclaimer, 95):
        c.drawString(LEFT, y, line)
        y -= 0.55 * cm

    # ================= SIGNATURE =================
    y -= 0.8 * cm
    c.drawString(LEFT, y, "Regards,")
    y -= 0.7 * cm
    c.drawString(LEFT, y, "Credit Team")
    y -= 0.6 * cm
    c.drawString(LEFT, y, "Tata Capital (Demo)")

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(
        width / 2,
        1.5 * cm,
        "This is a system-generated document. No physical signature is required."
    )

    c.showPage()
    c.save()

    return {
        "loan_id": loan_id,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "tenure": f"{tenure_months} months",
        "emi": emi,
        "file_path": file_path
    }
