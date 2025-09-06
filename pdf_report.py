from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

def generate_pdf_report(lat, lon, kmz_name, png_name, tif_name, lst_name):
    os.makedirs("outputs/pdf", exist_ok=True)
    filename = f"outputs/pdf/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "VoidBot Analysis Report")

    c.setFont("Helvetica", 12)
    y = height - 100
    line_height = 20

    c.drawString(50, y, f"Coordinates: Latitude = {lat}, Longitude = {lon}"); y -= line_height
    c.drawString(50, y, f"KMZ File: {kmz_name}"); y -= line_height
    c.drawString(50, y, f"Metal PNG: {png_name}"); y -= line_height
    c.drawString(50, y, f"GeoTIFF File: {tif_name}"); y -= line_height
    c.drawString(50, y, f"LST PNG: {lst_name}"); y -= line_height

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 40, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.save()
    return filename