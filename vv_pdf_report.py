# فایل: vv_pdf_report.py – ساخت گزارش PDF کامل تحلیل‌ها

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from pathlib import Path
import os

# ورودی‌ها: نام فایل‌های خروجی

def generate_pdf_report(lat, lon, kmz_file, png_file, geotiff_file, lst_file):
    styles = getSampleStyleSheet()
    doc_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = Path("outputs/pdf") / doc_name
    Path("outputs/pdf").mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []

    # عنوان
    story.append(Paragraph("<b>VoidVision ONE&trade; - گزارش تحلیل نهایی</b>", styles['Title']))
    story.append(Spacer(1, 12))

    # اطلاعات موقعیت
    story.append(Paragraph(f"تاریخ: {datetime.now().strftime('%Y/%m/%d')}", styles['Normal']))
    story.append(Paragraph(f"مختصات: lat={lat}, lon={lon}", styles['Normal']))
    story.append(Spacer(1, 12))

    # جدول فایل‌های خروجی
    story.append(Paragraph("<b>خروجی‌ها:</b>", styles['Heading3']))
    story.append(Paragraph(f"✅ تصویر تشخیص فضای خالی: {png_file}", styles['Normal']))
    story.append(Paragraph(f"✅ نقشه حرارتی LST: {lst_file}", styles['Normal']))
    story.append(Paragraph(f"✅ فایل ژئوتیف GeoTIFF: {geotiff_file}", styles['Normal']))
    story.append(Paragraph(f"✅ فایل Google Earth (KMZ): {kmz_file}", styles['Normal']))
    story.append(Spacer(1, 12))

    # پیش‌نمایش تصویر
    image_path = Path("outputs/png") / png_file
    if image_path.exists():
        story.append(Paragraph("<b>پیش‌نمایش تصویری:</b>", styles['Heading3']))
        story.append(RLImage(str(image_path), width=400, height=300))

    story.append(Spacer(1, 24))
    story.append(Paragraph("<i>این گزارش به‌صورت خودکار توسط سیستم VoidVision ONE™ تولید شده است.</i>", styles['Normal']))

    doc.build(story)
    return str(output_path)