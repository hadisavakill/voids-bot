
import streamlit as st
import subprocess
import re
import os
import csv
from datetime import datetime
from fpdf import FPDF

# ====== ایجاد پوشه‌ها در صورت عدم وجود ======
os.makedirs("outputs/kmz/advanced", exist_ok=True)
os.makedirs("outputs/png", exist_ok=True)
os.makedirs("outputs/geotiff", exist_ok=True)
os.makedirs("outputs/pdf", exist_ok=True)

def parse_coordinates(text):
    try:
        if "°" in text or "'" in text:
            parts = re.findall(r"(\d+)[°'](\d+)?", text)
            if len(parts) >= 2:
                lat = float(parts[0][0]) + float(parts[0][1]) / 60
                lon = float(parts[1][0]) + float(parts[1][1]) / 60
                return lat, lon
        else:
            lat, lon = map(float, text.split(","))
            return lat, lon
    except:
        return None, None

def log_analysis(lat, lon, radius, success, kmz, png, tif, lst_png, pdf, t1="", t2="", t3=""):
    log_path = "data/field_logs.csv"
    timestamp = datetime.now().isoformat()
    row = [timestamp, lat, lon, radius, success, kmz, png, tif, lst_png, pdf, t1, t2, t3]
    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "latitude", "longitude", "radius", "analysis_success", "kmz_file", "png_file", "geotiff_file", "lst_png", "pdf_report", "T1", "T2", "T3"])
        writer.writerow(row)

def get_latest_file(folder, ext):
    if not os.path.exists(folder):
        return "", ""
    files = [f for f in os.listdir(folder) if f.endswith(ext)]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    if files:
        return os.path.join(folder, files[0]), files[0]
    return "", ""

def generate_pdf_report(lat, lon, kmz_name, png_name, tif_name, lst_name):
    pdf_path = f"outputs/pdf/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="VoidBot گزارش تحلیل منطقه", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"مختصات: Latitude = {lat}, Longitude = {lon}", ln=True)
    pdf.cell(200, 10, txt=f"فایل KMZ: {kmz_name}", ln=True)
    pdf.cell(200, 10, txt=f"تصویر فلزات: {png_name}", ln=True)
    pdf.cell(200, 10, txt=f"تصویر GeoTIFF: {tif_name}", ln=True)
    pdf.cell(200, 10, txt=f"تصویر حرارتی LST: {lst_name}", ln=True)
    pdf.output(pdf_path)
    return pdf_path

# ================== رابط کاربری ==================
st.set_page_config(page_title="Void & Metal & Thermal Detector", layout="centered")
st.title("🛰️ تشخیص فضای خالی، فلزات و حرارتی (LST)")
st.markdown("---")
st.subheader("📍 وارد کردن مختصات")

void_input = st.text_input("✏️ مختصات (مثلاً: 35.82,59.91 یا N 59°54' E 35°35')", key="void")
radius = st.number_input("📏 شعاع تحلیل (متر)", min_value=10, max_value=1000, value=100)

if st.button("🚀 اجرای تحلیل کامل"):
    lat, lon = parse_coordinates(void_input)
    if lat and lon:
        st.info(f"در حال اجرای تحلیل برای lat={lat}, lon={lon}, radius={radius}")

        # اجرای اسکریپت‌ها
        result_void = subprocess.run(f"python export_void_kmz.py --lat {lat} --lon {lon} --radius {radius}", shell=True)
        result_metal = subprocess.run(f"python metal_indices.py --lat {lat} --lon {lon} --radius {radius}", shell=True)
        result_lst = subprocess.run(f"python lst_analyze.py", shell=True)

        # فایل‌های خروجی
        kmz_path, kmz_name = get_latest_file("outputs/kmz/advanced", ".kmz")
        png_path, png_name = get_latest_file("outputs/png", ".png")
        tif_path, tif_name = get_latest_file("outputs/geotiff", ".tif")
        lst_path, lst_name = get_latest_file("outputs/png", "lst")  # assuming lst images start with 'lst'

        # نمایش خروجی‌ها
        if kmz_path:
            with open(kmz_path, "rb") as f:
                st.success("✅ فایل KMZ ساخته شد.")
                st.download_button("📥 دانلود فایل KMZ", data=f, file_name=kmz_name, mime="application/vnd.google-earth.kmz")
        if png_path:
            with open(png_path, "rb") as f:
                st.image(png_path, caption="📷 تصویر فلزات", use_column_width=True)
                st.download_button("📥 دانلود تصویر PNG", data=f, file_name=png_name, mime="image/png")
        if tif_path:
            with open(tif_path, "rb") as f:
                st.download_button("📥 دانلود فایل GeoTIFF", data=f, file_name=tif_name, mime="image/tiff")
        if lst_path:
            with open(lst_path, "rb") as f:
                st.image(lst_path, caption="🌡️ تصویر حرارتی LST", use_column_width=True)
                st.download_button("📥 دانلود LST", data=f, file_name=lst_name, mime="image/png")

        # ساخت PDF گزارش
        pdf_path = generate_pdf_report(lat, lon, kmz_name, png_name, tif_name, lst_name)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 دانلود گزارش PDF", data=f, file_name=os.path.basename(pdf_path), mime="application/pdf")

        # ثبت لاگ
        log_analysis(lat, lon, radius, True, kmz_name, png_name, tif_name, lst_name, os.path.basename(pdf_path))

    else:
        st.warning("⚠️ مختصات نامعتبر است.")
st.markdown("---")
st.caption("📦 voids-bot | اجرای کامل تحلیل میدان، فلزات، حرارت و گزارش")
