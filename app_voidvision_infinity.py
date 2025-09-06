# فایل: app_voidvision_x_infinity.py – نسخه نهایی VoidVision X ∞ (Infinity Edition)

import streamlit as st
import os
import subprocess
import pandas as pd
import torch
import speech_recognition as sr
from PIL import Image
from datetime import datetime
from streamlit_folium import st_folium
import folium
import pydeck as pdk
from hashlib import sha256

st.set_page_config(page_title="VoidVision X ∞", layout="wide")
st.title("🛰️ VoidVision X ∞ – نسخه نهایی خودکار، هوشمند، و شکست‌ناپذیر")

# ساخت پوشه‌ها
for folder in ["outputs", "data", "outputs/png", "outputs/pdf", "outputs/geotiff", "outputs/kmz/advanced"]:
    os.makedirs(folder, exist_ok=True)

# فرمان صوتی
st.subheader("🗣️ فرمان صوتی")
if st.button("🎤 گوش دادن برای فرمان تحلیل"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("در حال گوش دادن... صحبت کن!")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='fa-IR')
        st.success(f"✅ تشخیص داده شد: {text}")
        if "تحلیل" in text:
            subprocess.run("python master_run.py", shell=True)
    except Exception as e:
        st.error(f"❌ خطا در تشخیص فرمان صوتی: {e}")

# انتخاب موقعیت از نقشه
st.subheader("🗺️ انتخاب موقعیت روی نقشه")
def pick_location():
    m = folium.Map(location=[35.82, 59.91], zoom_start=12)
    out = st_folium(m, height=400, width=700)
    return out.get("last_clicked") or {"lat": 35.82, "lng": 59.91}

coords = pick_location()
lat, lon = coords["lat"], coords["lng"]
radius = st.slider("📏 شعاع تحلیل (متر)", 40, 200, 100)

# اجرای کامل تحلیل
if st.button("🚀 اجرای تحلیل کامل VoidVision X"):
    st.info("اجرای کامل در حال انجام است...")
    command = f"python master_run.py"
    subprocess.run(command, shell=True)
    now = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_csv("data/logs.csv") if os.path.exists("data/logs.csv") else pd.DataFrame(columns=["date", "lat", "lon", "radius"])
    df.loc[len(df)] = [now, lat, lon, radius]
    df.to_csv("data/logs.csv", index=False)
    st.success("✅ تحلیل کامل شد.")

# نمایش خروجی 3D
st.subheader("🌐 نمایش سه‌بعدی")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame({"lat": [lat], "lon": [lon]}),
    get_position='[lon, lat]',
    get_color='[255, 0, 0]',
    get_radius=radius
)
view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=15, pitch=50)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# خروجی‌ها
st.subheader("📦 دانلود فایل‌ها")
for folder, ext in [("outputs/pdf", ".pdf"), ("outputs/png", ".png"), ("outputs/geotiff", ".tif"), ("outputs/kmz/advanced", ".kmz")]:
    for f in os.listdir(folder):
        if f.endswith(ext):
            with open(os.path.join(folder, f), "rb") as file:
                st.download_button(f"⬇️ {f}", file, file_name=f)

# امنیت فایل PDF
st.subheader("🔐 امضای دیجیتال PDF")
pdfs = sorted([f for f in os.listdir("outputs/pdf") if f.endswith(".pdf")], key=lambda x: os.path.getmtime(os.path.join("outputs/pdf", x)), reverse=True)
if pdfs:
    last_pdf = os.path.join("outputs/pdf", pdfs[0])
    pdf_hash = sha256(open(last_pdf, "rb").read()).hexdigest()
    st.code(f"SHA256: {pdf_hash}")

# تاریخچه هوشمند
st.subheader("🧬 تاریخچه تحلیل‌ها")
if os.path.exists("data/logs.csv"):
    df = pd.read_csv("data/logs.csv")
    st.dataframe(df)
else:
    st.info("⛔ تاکنون تحلیلی ثبت نشده است.")