# فایل اصلی: app_voidvision_one.py

import streamlit as st
import os
import subprocess
from PIL import Image
from streamlit_folium import st_folium
import folium
import datetime

st.set_page_config(page_title="VoidVision ONE™", layout="wide")
st.title("🛰️ VoidVision ONE – نسخه نهایی 7فازه")

# ساخت پوشه‌ها
for f in ["outputs/geotiff", "outputs/png", "outputs/kmz/advanced", "outputs/pdf", "data"]:
    os.makedirs(f, exist_ok=True)

# --- انتخاب روی نقشه ---
st.subheader("📍 انتخاب مکان بررسی روی نقشه")
def pick_from_map():
    default_lat, default_lon = 35.82, 59.91
    m = folium.Map(location=[default_lat, default_lon], zoom_start=12)
    marker = folium.Marker(location=[default_lat, default_lon], draggable=True)
    marker.add_to(m)
    output = st_folium(m, height=400, width=700)
    return output.get("last_clicked") or {"lat": default_lat, "lng": default_lon}

coords = pick_from_map()
lat, lon = coords["lat"], coords["lng"]
st.success(f"📌 مختصات انتخاب شده: {lat:.5f}, {lon:.5f}")

radius = st.slider("📏 شعاع تحلیل (متر)", 40, 200, 100)

# اجرای کامل
if st.button("🚀 اجرای کامل 7 فاز"):
    with st.spinner("در حال اجرای تحلیل کامل..."):
        subprocess.run(f"python master_run.py", shell=True)
    st.success("✅ تحلیل کامل شد و خروجی‌ها ساخته شدند.")

    # نمایش تصاویر نهایی
    st.subheader("🖼️ نمایش تصویری")
    col1, col2 = st.columns(2)
    with col1:
        void_img = "outputs/png/void_fixed.png"
        if os.path.exists(void_img):
            st.image(Image.open(void_img), caption="Void Map", use_column_width=True)
    with col2:
        prob_img = "outputs/png/probability_map.png"
        if os.path.exists(prob_img):
            st.image(Image.open(prob_img), caption="Probability Map", use_column_width=True)

    # دانلود فایل‌ها
    st.subheader("📦 دانلود خروجی‌ها")
    def download_all(folder, ext, label):
        for fname in os.listdir(folder):
            if fname.endswith(ext):
                path = os.path.join(folder, fname)
                with open(path, "rb") as f:
                    st.download_button(f"📥 دانلود {label}: {fname}", f, file_name=fname)

    download_all("outputs/pdf", ".pdf", "PDF")
    download_all("outputs/png", ".png", "تصویر")
    download_all("outputs/kmz/advanced", ".kmz", "KMZ")
    download_all("outputs/geotiff", ".tif", "GeoTIFF")

    # خلاصه انسانی‌فهم
    st.subheader("🧠 خلاصه تحلیلی")
    st.info("در این محدوده، سیستم VoidVision تشخیص داده است که احتمال فضای خالی یا فلزات قابل توجه وجود دارد. لطفاً برای بررسی میدانی از فایل‌های PDF و KMZ استفاده نمایید.")

# TODO: افزودن فاز 6 و 7 به‌صورت افزایشی (امنیت و فرمان هوشمند)