# generate_report.py
from fpdf import FPDF
import datetime
import os

def generate_pdf_report(lat, lon, analysis_type, image_path, output_path="reports/pdf/report.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    # عنوان
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "گزارش تحلیل باستان‌شناسی", ln=True, align="C")

    pdf.ln(10)

    # اطلاعات کلی
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"🔹 نوع تحلیل: {analysis_type}", ln=True)
    pdf.cell(0, 10, f"📍 مختصات: {lat}, {lon}", ln=True)
    pdf.cell(0, 10, f"📅 تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    pdf.ln(10)

    # تصویر خروجی
    if os.path.exists(image_path):
        pdf.image(image_path, x=30, w=150)
    else:
        pdf.cell(0, 10, "❌ تصویر پیدا نشد.", ln=True)

    pdf.ln(10)

    # توضیح تحلیلی
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, f"""
این گزارش بر اساس داده‌های سنجش از دور و شاخص‌های تحلیلی مانند NDVI، NDWI، VOID یا METAL تهیه شده است.
نتایج ارائه‌شده به صورت اولیه بوده و برای استفاده میدانی نیاز به اعتبارسنجی بیشتر دارد.
""")

    # ذخیره
    pdf.output(output_path)
    print(f"✅ گزارش PDF ساخته شد: {output_path}")

# 🧪 تست
if __name__ == "__main__":
    generate_pdf_report(
        lat=35.82472,
        lon=59.91532,
        analysis_type="فضای خالی (VOID)",
        image_path="outputs/png/void_map.png"
    )