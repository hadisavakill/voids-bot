import streamlit as st
import os
import subprocess
import time
from PIL import Image

st.set_page_config(page_title="VoidBot | تشخیص فضای خالی و فلزات", layout="wide")
st.title("🛰️ VoidBot | تشخیص فضای خالی و فلزات زیرزمینی")

st.markdown("### 🗺️ مختصات منطقه را وارد کنید")

lat = st.number_input("🌐 عرض جغرافیایی (latitude)", value=35.82, format="%.6f")
lon = st.number_input("🌐 طول جغرافیایی (longitude)", value=59.91, format="%.6f")
radius = st.slider("📏 شعاع تحلیل (متر)", 40, 200, 100)

run_analysis = st.button("🚀 اجرای تحلیل")

if run_analysis:
    with st.spinner("در حال اجرای تحلیل..."):
        command = f"python master_run.py"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output:
                st.text(output.decode("utf-8").strip())
            elif process.poll() is not None:
                break
        st.success("✅ تحلیل کامل شد.")

    st.markdown("---")
    st.markdown("### 🖼️ نتایج تصویری")

    png_folder = "outputs/png"
    kmz_folder = "outputs/kmz/advanced"

    col1, col2 = st.columns(2)

    with col1:
        void_path = os.path.join(png_folder, "void_fixed.png")
        if os.path.exists(void_path):
            st.image(Image.open(void_path), caption="Void Map", use_column_width=True)

    with col2:
        prob_path = os.path.join(png_folder, "probability_map.png")
        if os.path.exists(prob_path):
            st.image(Image.open(prob_path), caption="Probability Map", use_column_width=True)

    st.markdown("### 📥 دانلود خروجی‌ها")

    # KMZ
    for fname in os.listdir(kmz_folder):
        if fname.endswith(".kmz") and "void_overlay" in fname:
            kmz_path = os.path.join(kmz_folder, fname)
            with open(kmz_path, "rb") as f:
                st.download_button("🌍 دانلود فایل KMZ", f, file_name=fname)

    # PDF
    pdf_folder = "outputs/pdf"
    for fname in os.listdir(pdf_folder):
        if fname.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, fname)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 دانلود گزارش PDF", f, file_name=fname)

    # GeoTIFF
    tif_folder = "outputs/geotiff"
    for fname in os.listdir(tif_folder):
        if fname.endswith(".tif") and "void" in fname:
            tif_path = os.path.join(tif_folder, fname)
            with open(tif_path, "rb") as f:
                st.download_button("🗺️ دانلود Void GeoTIFF", f, file_name=fname)

    st.success("🎉 تحلیل و خروجی‌ها با موفقیت انجام شد.")