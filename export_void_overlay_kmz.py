import os
import zipfile
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Generate KMZ with image overlay for Google Earth")
parser.add_argument("--lat", type=float, required=True, help="مرکز عرض جغرافیایی")
parser.add_argument("--lon", type=float, required=True, help="مرکز طول جغرافیایی")
parser.add_argument("--radius", type=int, default=100, help="شعاع تصویر به متر")
parser.add_argument("--image", type=str, default="outputs/png/void_latest.png", help="مسیر تصویر PNG")
args = parser.parse_args()

lat, lon, radius = args.lat, args.lon, args.radius
image_path = args.image

if not os.path.exists(image_path):
    raise FileNotFoundError(f"تصویر یافت نشد: {image_path}")

# تبدیل شعاع متر به درجه تقریبی (0.0009 ≈ 100m)
delta_deg = radius * 0.000009

north = lat + delta_deg
south = lat - delta_deg
east = lon + delta_deg
west = lon - delta_deg

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = "outputs/kmz/overlay"
os.makedirs(output_folder, exist_ok=True)

kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <GroundOverlay>
    <name>Void Overlay</name>
    <Icon>
      <href>overlay.png</href>
    </Icon>
    <LatLonBox>
      <north>{north}</north>
      <south>{south}</south>
      <east>{east}</east>
      <west>{west}</west>
    </LatLonBox>
  </GroundOverlay>
</kml>
"""

kml_path = os.path.join(output_folder, "doc.kml")
with open(kml_path, "w", encoding="utf-8") as f:
    f.write(kml_content)

# کپی تصویر به آنجا
image_copy_path = os.path.join(output_folder, "overlay.png")
with open(image_path, "rb") as src, open(image_copy_path, "wb") as dst:
    dst.write(src.read())

# ساخت KMZ
kmz_filename = f"void_overlay_{lat}_{lon}_{timestamp}.kmz"
kmz_path = os.path.join(output_folder, kmz_filename)

with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as kmz:
    kmz.write(kml_path, arcname="doc.kml")
    kmz.write(image_copy_path, arcname="overlay.png")

# پاک کردن فایل‌های موقت
os.remove(kml_path)
os.remove(image_copy_path)

print(f"✅ فایل KMZ تصویری ساخته شد: {kmz_path}")