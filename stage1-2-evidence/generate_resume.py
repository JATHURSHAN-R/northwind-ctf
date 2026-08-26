"""
Generates resume.pdf for Stage 1 and embeds the flag in the PDF's
Author/Comments metadata via exiftool (findable with `exiftool resume.pdf`
or a browser's Document Properties panel, per the stage spec).
"""
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = "site/blog/resume.pdf"
FLAG = "NW{m3tadata_n3v3r_l1es}"

c = canvas.Canvas(OUT, pagesize=A4)
width, height = A4

c.setFont("Helvetica-Bold", 18)
c.drawString(60, height - 80, "Ravi Chandran")
c.setFont("Helvetica", 11)
c.drawString(60, height - 100, "Systems Administrator")

c.setFont("Helvetica-Bold", 13)
c.drawString(60, height - 140, "Experience")
c.setFont("Helvetica", 10)
lines = [
    "Northwind Logistics -- Systems Administrator (6 years)",
    "  Managed on-prem infrastructure: Windows Server, Linux, network services.",
    "  Administered internal portal, mail server, and database systems.",
    "",
    "Skills",
    "  Windows Server, Linux administration, SQL, networking, scripting.",
    "",
    "References available on request.",
]
y = height - 165
for line in lines:
    c.drawString(60, y, line)
    y -= 16

c.save()

# Embed the flag in document metadata -- not visible on the rendered page.
# (PDF metadata via exiftool: Subject/Keywords are the writable fields that
# show up in "Document Properties" -- Comments is not a valid PDF tag.)
subprocess.run([
    "exiftool", "-overwrite_original",
    f"-Author=Ravi Chandran",
    f"-Subject={FLAG}",
    OUT,
], check=True)

print("Resume PDF generated with flag in metadata.")
