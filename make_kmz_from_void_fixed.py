import os
import zipfile
from datetime import datetime
from pathlib import Path
import shutil

# مسیر فایل تصویری
image_name = "void_fixed.png"
image_path = Path("outputs/png") / image_name

# مسیر خروجی
output_folder = Path("outputs/kmz/advanced")
output_folder.mkdir(parents=True, exist_ok=True)

# مختصات برای نمایش تصویر روی زمین (قابل تنظیم دستی)
north, south = 35.83, 35.81
east, west = 59.92, 59.90

# تولید فایل kml
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_name = f"void_overlay_{timestamp}"
kml_path = output_folder / f"{base_name}.kml"

kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Folder>
    <name>VoidBot Map</name>
    <GroundOverlay>
      <Icon>
        <href>{image_name}</href>
      </Icon>
      <LatLonBox>
        <north>{north}</north>
        <south>{south}</south>
        <east>{east}</east>
        <west>{west}</west>
      </LatLonBox>
    </GroundOverlay>
  </Folder>
</kml>
"""
with open(kml_path, "w", encoding="utf-8") as f:
    f.write(kml_content)

# کپی تصویر
copied_image = output_folder / image_name
shutil.copy(image_path, copied_image)

# ساخت فایل KMZ
kmz_path = output_folder / f"{base_name}.kmz"
with zipfile.ZipFile(kmz_path, "w") as kmz:
    kmz.write(kml_path, arcname="doc.kml")
    kmz.write(copied_image, arcname=image_name)

# حذف فایل‌های موقت
copied_image.unlink()
kml_path.unlink()

print("✅ KMZ ساخته شد:", kmz_path.name)