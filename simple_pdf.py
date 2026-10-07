from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Create a more comprehensive PDF
pdf_path = "/root/provenance/PITCH_DECK.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

styles = getSampleStyleSheet()
title_style = styles['Title']
heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], spaceAfter=12)
body_style = styles['Normal']

story = []

# Title
story.append(Paragraph("Provenance", title_style))
story.append(Spacer(1, 20))
story.append(Paragraph("<b>Payment holds where the ledger refuses an invented cause</b>", body_style))
story.append(Paragraph("HackCanton Season 4 • Track 1: RWA & Business Workflows", body_style))
story.append(Spacer(1, 30))

# The Problem
story.append(Paragraph("The Problem", heading_style))
story.append(Paragraph("When payment rails freeze funds, they say 'ON HOLD' but not WHY. Recipients guess and make costly mistakes.", body_style))
story.append(Spacer(1, 10))
story.append(Paragraph("<b>Real impacts from 4 interviews (Oct 2026):</b>", body_style))

interviews = [
    "Freelancer: $850 held 9 days → split to dodge → account flagged",
    "Agency: $2,400 held 14 days → paid from savings → double-paid",
    "Engineer: $4,200 held 6 days → webhook returned reason:null → API keys revoked",
    "Contractor: $1,650 held 8 days → opened tickets → lost queue position"
]
for i in interviews:
    story.append(Paragraph(f"• {i}", body_style))
story.append(Spacer(1, 20))

# The Solution
story.append(Paragraph("The Solution", heading_style))
story.append(Paragraph("<b>Provenance = Canton Ledger enforcing honesty</b> — where \"don't invent a reason\" isn't a promise but a cryptographic rule.", body_style))
story.append(Spacer(1, 10))

features = [
    "No 'reason' field to fabricate",
    "Both parties must sign for release",
    "Auditor can verify without seeing private data", 
    "Stranger sees NOTHING"
]
for f in features:
    story.append(Paragraph(f"• {f}", body_style))

# Demo
story.append(Spacer(1, 30))
story.append(Paragraph("Live Demo", heading_style))
story.append(Paragraph("GitHub: github.com/HusseinAdeiza/provenance", body_style))
story.append(Paragraph("Demo: provenance-demo.onrender.com", body_style))

doc.build(story)
print(f"Created comprehensive {pdf_path}")