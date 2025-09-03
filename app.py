import streamlit as st
import subprocess
from datetime import date

st.set_page_config(page_title="Void & Metal Detector", layout="centered")

st.title("📍 سیستم تشخیص فضای خالی و فلزات")
st.markdown("برای شروع، مختصات و تنظیمات را وارد کنید:")

mode = st.selectbox("🔍 نوع تحلیل", ["rgb", "ndvi", "ndwi", "void", "metal"])
lat = st.number_input("🌐 عرض جغرافیایی (Latitude)", value=35.82505, format="%.5f")
lon = st.number_input("🌐 طول جغرافیایی (Longitude)", value=59.91487, format="%.5f")
radius = st.number_input("📏 شعاع تحلیل (متر)", value=300, step=50)
date_from = st.date_input("📅 از تاریخ", value=date(2024, 8, 1))
date_to   = st.date_input("📅 تا تاریخ", value=date(2025, 8, 1))

if st.button("🚀 اجرا"):
    cmd = f"python subsurface_analyze.py --mode {mode} --lat {lat} --lon {lon} --radius {radius} --from {date_from} --to {date_to}"
    st.code(cmd, language="bash")
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        st.success("✅ تحلیل با موفقیت انجام شد.")
        st.text(result)
    except subprocess.CalledProcessError as e:
        st.error("❌ خطا در اجرای تحلیل.")
        st.text(e.output)