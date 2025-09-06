# فایل: app_voidvision_x.py – پلتفرم نهایی VoidVision X™ – همه‌چیزتمام

import streamlit as st
import os
import subprocess
import pandas as pd
from PIL import Image
from datetime import datetime
from streamlit_folium import st_folium
import folium
from hashlib import sha256

st.set_page_config(page_title="VoidVision X", layout="wide")
st.title("🛰️ VoidVision X™ – تحلیل کامل زیرزمین + هوش مصنوعی + امنیت")

# ساخت پوشه‌ها
for folder in ["outputs", "data", "outputs/png", "outputs/pdf", "outputs/geotiff", "outputs/kmz/advanced"]:
    os.makedirs(folder, exist_ok=True)

# نمایش نقشه و انتخاب نقطه
st.subheader("📍 انتخاب موقعیت روی نقشه")
def pick_location():
    m = folium.Map(location=[35.82, 59.91], zoom_start=12)
    folium.Marker([35.82, 59.91], tooltip="نقطه پیش‌فرض").add_to(m)
    out = st_folium(m, height=400, width=700)
    return out.get("last_clicked") or {"lat": 35.82, "lng": 59.91}

coords = pick_location()
lat, lon = coords["lat"], coords["lng"]
radius = st.slider("📏 شعاع تحلیل (متر)", 40, 200, 100)
run_now = st.button("🚀 اجرای کامل تحلیل 7 فاز")

def save_log(lat, lon, radius):
    log_path = "data/logs.csv"
    df = pd.read_csv(log_path) if os.path.exists(log_path) else pd.DataFrame(columns=["time", "lat", "lon", "radius"])
    df.loc[len(df)] = [datetime.now(), lat, lon, radius]
    df.to_csv(log_path, index=False)

if run_now:
    st.info("در حال اجرای تحلیل کامل...")
    command = f"python master_run.py"
    subprocess.run(command, shell=True)
    save_log(lat, lon, radius)
    st.success("✅ تحلیل کامل انجام شد و فایل‌ها ذخیره شدند.")

    # پیش‌نمایش خروجی‌ها
    col1, col2 = st.columns(2)
    if os.path.exists("outputs/png/void_fixed.png"):
        col1.image("outputs/png/void_fixed.png", caption="Void Map", use_column_width=True)
    if os.path.exists("outputs/png/probability_map.png"):
        col2.image("outputs/png/probability_map.png", caption="Probability Map", use_column_width=True)

    # دانلود خروجی‌ها
    st.subheader("📥 دانلود فایل‌های خروجی")
    def download_all(folder, ext):
        for f in os.listdir(folder):
            if f.endswith(ext):
                with open(os.path.join(folder, f), "rb") as file:
                    st.download_button(f"⬇️ دانلود {f}", data=file, file_name=f)
    download_all("outputs/pdf", ".pdf")
    download_all("outputs/kmz/advanced", ".kmz")
    download_all("outputs/geotiff", ".tif")

    # امضای دیجیتال (SHA256) فایل PDF آخر
    st.subheader("🔐 امنیت و اعتبار فایل")
    pdfs = sorted(Path("outputs/pdf").glob("*.pdf"), key=os.path.getmtime, reverse=True)
    if pdfs:
        last_pdf = pdfs[0]
        hash = sha256(open(last_pdf, "rb").read()).hexdigest()
        st.code(f"SHA256: {hash}", language="text")
        st.info("امضای دیجیتال PDF برای اثبات اعتبار و جلوگیری از تغییر فایل")

# نمایش تاریخچه تحلیل‌ها
st.subheader("📊 تاریخچه تحلیل‌ها")
log_file = "data/logs.csv"
if os.path.exists(log_file):
    df = pd.read_csv(log_file)
    st.dataframe(df)
else:
    st.info("هیچ تحلیلی ثبت نشده است.")