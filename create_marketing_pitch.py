from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_marketing_pitch_pdf():
    pdf_path = r"D:\Users\CogCulture_PM_Assessment\part2_fact_check_agent\CogCulture_Fintech_Pitch_2026.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawString(54, height - 60, "Fintech & Digital Payments Growth Deck 2026")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#3B82F6"))
    c.drawString(54, height - 80, "CONFIDENTIAL INVESTOR MEMORANDUM | COG CULTURE CASE STUDY")

    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(54, height - 90, width - 54, height - 90)

    claims = [
        "Strategic Market Overview:",
        "This memorandum provides a market assessment of global digital banking, UPI ecosystems, and payment infrastructures.",
        "",
        "Key Market Projections & Performance Claims:",
        "1. India's Unified Payments Interface (UPI) processed over 130 Billion transactions in the calendar year 2023.",
        "   (Verified Baseline: Corroborated by National Payments Corporation of India (NPCI) official releases).",
        "",
        "2. Stripe Inc. reached an all-time private market valuation of $450 Billion USD in its Series I funding round in 2024.",
        "   (Exaggerated Claim: Stripe's actual valuation was ~$65 - $70 Billion, down from its peak of $95B).",
        "",
        "3. Nvidia Corporation surpassed a $3.0 Trillion USD market valuation in June 2024, briefly becoming the world's most valuable company.",
        "   (Verified Fact: Public NASDAQ trading data and global financial press records).",
        "",
        "4. According to Gartner, 99.8% of all Fortune 500 enterprises have completely decommissioned relational SQL databases in 2025.",
        "   (Hallucinated Stat: Grossly fabricated claim - relational databases remain standard enterprise infrastructure).",
        "",
        "Conclusion & Auditor Summary:",
        "All factual statements must be cross-referenced against live financial registries and authoritative web intelligence."
    ]

    y = height - 120
    for line in claims:
        if line.startswith("Strategic Market Overview:") or line.startswith("Key Market Projections") or line.startswith("Conclusion"):
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor("#0F172A"))
        elif line.strip().startswith("(") and line.strip().endswith(")"):
            c.setFont("Helvetica-Oblique", 8.5)
            c.setFillColor(colors.HexColor("#64748B"))
        elif line == "":
            y -= 6
            continue
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.HexColor("#1E293B"))

        c.drawString(54, y, line)
        y -= 18

    c.save()
    print(f"Created new marketing pitch test PDF: {pdf_path}")

if __name__ == "__main__":
    create_marketing_pitch_pdf()
