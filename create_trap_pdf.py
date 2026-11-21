from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_trap_pdf():
    pdf_path = r"D:\Users\CogCulture_PM_Assessment\part2_fact_check_agent\CogCulture_Trap_Document_Test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawString(54, height - 60, "Global Technology & AI Market Benchmark Report 2026")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#6366F1"))
    c.drawString(54, height - 80, "CONFIDENTIAL & PROPRIETARY  |  PREPARED FOR COG CULTURE ASSESSMENT EVALUATION")

    c.setLineWidth(1)
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(54, height - 90, width - 54, height - 90)

    # Body claims
    c.setFont("Helvetica", 10.5)
    c.setFillColor(colors.HexColor("#1E293B"))

    claims = [
        "Executive Summary:",
        "This evaluation report presents cross-industry market statistics across global software, artificial intelligence,",
        "and public technology enterprises for fact-checking and automated accuracy validation.",
        "",
        "Key Quantitative Findings & Market Assertions:",
        "1. According to official corporate records, Apple Inc. was founded in the year 1995 in Silicon Valley by Mark Zuckerberg.",
        "   (Intentional Trap: Historical entity lie - founded in 1976 by Steve Jobs & Steve Wozniak).",
        "",
        "2. Microsoft Corporation achieved unprecedented growth as its market cap surpassed $12.5 Trillion USD in Q1 2026.",
        "   (Intentional Trap: Grossly inflated figure - actual market cap is ~$3.1 - $3.3 Trillion).",
        "",
        "3. OpenAI's ChatGPT achieved 100 million monthly active users in January 2023, just two months after its launch,",
        "   ranking as the fastest-growing consumer application in internet history.",
        "   (Real Fact: True baseline benchmark corroborated across Reuters and UBS data).",
        "",
        "4. In its fiscal year 2023 earnings report, Alphabet Inc. reported annual advertising revenue exceeding $950 Billion USD.",
        "   (Intentional Trap: Outdated/distorted stat - total Alphabet FY23 revenue was $307.4B, with Google ad revenue at $237.8B).",
        "",
        "5. Stack Overflow's annual developer census confirmed that Python achieved an overwhelming 85% developer market share,",
        "   officially making it the only programming language used in commercial AI systems.",
        "   (Intentional Trap: Fabricated market dominance - Python is ~51% on Stack Overflow).",
        "",
        "6. In mid-2024, the United States Federal Reserve raised benchmark interest rates to 25.5%, triggering a total global liquidity halt.",
        "   (Intentional Trap: Egregious hallucination - peak Fed funds rate reached ~5.25% - 5.50%).",
        "",
        "Conclusion:",
        "These metrics represent test vectors specifically designed to evaluate the Truth Layer Agent's parsing,",
        "live web cross-referencing, and real-fact correction engine."
    ]

    y = height - 120
    for line in claims:
        if line.startswith("Executive Summary:") or line.startswith("Key Quantitative Findings") or line.startswith("Conclusion:"):
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
    print(f"Trap PDF created at {pdf_path}")

if __name__ == "__main__":
    create_trap_pdf()
