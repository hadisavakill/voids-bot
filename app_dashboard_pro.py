# فایل: app_dashboard_pro.py

import streamlit as st
import os
import subprocess
import datetime
from streamlit_folium import st_folium
import folium
from PIL import Image

st.set_page_config(page_title="VoidBot PRO", layout="wide")
st.title("🛰️ VoidBot PRO – نسخه نهایی با نقشه ضد خطا")

# ساخت پوشه‌ها
for folder in ["outputs/kmz/advanced", "outputs/png", "outputs/geotiff", "outputs/pdf", "data"]:
    os.makedirs(folder, exist_ok=True)

# بارگذاری فایل لاگ
log_path = "data/field_logs.csv"
if os.path.exists(log_path):
    import pandas as pd
    df = pd.read_csv(log_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["radius"] = pd.to_numeric(df["radius"], errors="coerce")
else:
    df = pd.DataFrame(columns=[
        "timestamp", "latitude", "longitude", "radius", "analysis_success",
        "kmz_file", "png_file", "geotiff_file", "lst_png", "pdf_report"
    ])

# تحلیل جدید
st.header("🆕 تحلیل جدید")
coord_input = st.text_input("📍 مختصات", key="coord")
radius = st.number_input("📏 شعاع تحلیل (متر)", min_value=10, max_value=1000, value=100)

# تبدیل مختصات
import re
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

# پیدا کردن آخرین فایل در پوشه
def get_latest_file(folder, ext):
    files = [f for f in os.listdir(folder) if ext in f]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return (os.path.join(folder, files[0]), files[0]) if files else ("", "")

# اجرای تحلیل
if st.button("🚀 اجرای تحلیل"):
    lat, lon = parse_coordinates(coord_input)
    if lat and lon:
        subprocess.run(f"python export_void_kmz.py --lat {lat} --lon {lon} --radius {radius}", shell=True)
        subprocess.run(f"python metal_indices.py --lat {lat} --lon {lon} --radius {radius}", shell=True)
        subprocess.run("python lst_analyze.py", shell=True)

        kmz_path, kmz_name = get_latest_file("outputs/kmz/advanced", ".kmz")
        png_path, png_name = get_latest_file("outputs/png", ".png")
        tif_path, tif_name = get_latest_file("outputs/geotiff", ".tif")
        lst_path, lst_name = get_latest_file("outputs/png", "lst")

        # گزارش PDF
        from pdf_report import generate_pdf_report
        pdf_path = generate_pdf_report(lat, lon, kmz_name, png_name, tif_name, lst_name)

        with open(kmz_path, "rb") as f:
            st.download_button("🌍 دانلود KMZ", data=f, file_name=kmz_name)
        with open(png_path, "rb") as f:
            st.download_button("🧲 دانلود فلزات", data=f, file_name=png_name)
        with open(tif_path, "rb") as f:
            st.download_button("🗺️ دانلود GeoTIFF", data=f, file_name=tif_name)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 دانلود PDF", data=f, file_name=os.path.basename(pdf_path))

        if st.checkbox("👁️ نمایش تصویر فلزات"):
            st.image(Image.open(png_path), caption="فلزات", use_column_width=True)
        if st.checkbox("👁️ نمایش تصویر حرارتی"):
            st.image(Image.open(lst_path), caption="حرارتی", use_column_width=True)

# داشبورد تحلیل‌های قبلی
st.header("📊 تحلیل‌های قبلی")
if not df.empty:
    radius_values = df["radius"].dropna()
    radius_min = int(radius_values.min()) if not radius_values.empty else 10
    radius_max = int(radius_values.max()) if not radius_values.empty else 300

    with st.sidebar:
        date_range = st.date_input("📅 بازه زمانی", [df["timestamp"].min().date(), df["timestamp"].max().date()])
        radius_range = st.slider("📏 شعاع تحلیل", radius_min, radius_max, (radius_min, radius_max))
        search = st.text_input("🔎 جستجو")

    filtered = df[
        (df["timestamp"].dt.date >= date_range[0]) &
        (df["timestamp"].dt.date <= date_range[1]) &
        (df["radius"] >= radius_range[0]) &
        (df["radius"] <= radius_range[1])
    ]

    if search:
        filtered = filtered[
            filtered.apply(lambda r: search.lower() in str(r["latitude"]).lower() or
                                       search.lower() in str(r["longitude"]).lower() or
                                       search.lower() in str(r["kmz_file"]).lower() or
                                       search.lower() in str(r["pdf_report"]).lower(), axis=1)
        ]

    st.success(f"📄 {len(filtered)} تحلیل پیدا شد")

    for idx, row in filtered.iterrows():
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1:
            st.markdown(f"📍 `{row['latitude']}, {row['longitude']}`")
            st.markdown(f"📅 {row['timestamp']}")
            st.markdown(f"📏 شعاع: {row['radius']} متر")
        with c2:
            k_path = os.path.join("outputs/kmz/advanced", row["kmz_file"])
            p_path = os.path.join("outputs/pdf", row["pdf_report"])
            if os.path.exists(k_path):
                with open(k_path, "rb") as f:
                    st.download_button("🌍 دانلود KMZ", data=f, file_name=row["kmz_file"])
            if os.path.exists(p_path):
                with open(p_path, "rb") as f:
                    st.download_button("📄 دانلود PDF", data=f, file_name=row["pdf_report"])
        with c3:
            img_path = os.path.join("outputs/png", row["png_file"])
            if os.path.exists(img_path):
                try:
                    st.image(Image.open(img_path), caption="فلزات", width=150)
                except:
                    st.warning("تصویر قابل نمایش نیست.")

    st.markdown("### 🗺️ نقشه نقاط تحلیل‌شده")
    if not filtered[["latitude", "longitude"]].isna().any().any():
        map_center = [filtered["latitude"].mean(), filtered["longitude"].mean()]
        m = folium.Map(location=map_center, zoom_start=6)
        for _, row in filtered.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"{row['timestamp']} - شعاع {row['radius']}متر",
                tooltip="📍"
            ).add_to(m)
        st_folium(m, width=1200, height=500)
    else:
        st.info("📭 داده‌ای برای نمایش روی نقشه وجود ندارد.")
else:
    st.info("📭 هنوز تحلیلی انجام نشده.")