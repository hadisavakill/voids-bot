import argparse
import os
from datetime import datetime
import zipfile

# ورودی از کاربر
parser = argparse.ArgumentParser(description="Create KMZ for Google Earth")
parser.add_argument("--lat", type=float, required=True)
parser.add_argument("--lon", type=float, required=True)
parser.add_argument("--radius", type=int, default=100)
args = parser.parse_args()

lat, lon, radius = args.lat, args.lon, args.radius
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ساخت مسیر خروجی
output_folder = "outputs/kmz/advanced"
os.makedirs(output_folder, exist_ok=True)

# ساخت فایل KML استاندارد
kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Void Detection - {timestamp}</name>
    <Placemark>
      <name>Void Center</name>
      <description>Suspected void area with radius {radius} meters</description>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""

# مسیر ذخیره فایل‌ها
kml_filename = f"void_{lat}_{lon}_{radius}_{timestamp}.kml"
kml_path = os.path.join(output_folder, kml_filename)

with open(kml_path, "w", encoding="utf-8") as f:
    f.write(kml_content)

# تبدیل KML به KMZ
kmz_filename = kml_filename.replace(".kml", ".kmz")
kmz_path = os.path.join(output_folder, kmz_filename)

with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as kmz:
    kmz.write(kml_path, arcname="doc.kml")

# حذف فایل KML پس از فشرده‌سازی
os.remove(kml_path)

print(f"✅ فایل واقعی KMZ ساخته شد: {kmz_path}")