# فایل: vv_export_kmz.py – ساخت فایل KMZ برای Google Earth

import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

# پارامترهای ورودی برای تست (بعداً از اپ یا master_run دریافت می‌شوند)
image_name = "void_fixed.png"
image_path = Path("outputs/png") / image_name
lat, lon = 35.82, 59.91
side_deg = 0.0018  # حدود 200 متر (بسته به مختصات متغیر است)

# بررسی وجود تصویر
if not image_path.exists():
    print("❌ فایل تصویری موجود نیست:", image_path)
    exit(1)

# محاسبه مختصات کادر تصویر
north = lat + side_deg / 2
south = lat - side_deg / 2
east = lon + side_deg / 2
west = lon - side_deg / 2

# ساخت پوشه خروجی
output_dir = Path("outputs/kmz/advanced")
output_dir.mkdir(parents=True, exist_ok=True)

# ساخت فایل KML موقت
kml_path = output_dir / "temp_overlay.kml"
kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <GroundOverlay>
    <name>{image_name}</name>
    <Icon><href>{image_name}</href></Icon>
    <LatLonBox>
      <north>{north}</north>
      <south>{south}</south>
      <east>{east}</east>
      <west>{west}</west>
    </LatLonBox>
  </GroundOverlay>
</kml>"""
kml_path.write_text(kml_content)

# کپی تصویر موقت
img_copy = output_dir / image_name
shutil.copy(image_path, img_copy)

# ساخت فایل KMZ
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
kmz_path = output_dir / f"void_overlay_{timestamp}.kmz"
with zipfile.ZipFile(kmz_path, "w") as z:
    z.write(kml_path, arcname="doc.kml")
    z.write(img_copy, arcname=image_name)

# پاکسازی فایل‌های موقت
kml_path.unlink()
img_copy.unlink()

print(f"✅ فایل KMZ ساخته شد: {kmz_path.name}")