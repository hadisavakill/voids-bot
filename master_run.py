# فایل نهایی: master_run.py – هماهنگ با VoidVision ONE™

import os
import subprocess
from datetime import datetime

# ✅ پارامترهای مرکزی قابل تنظیم از رابط اصلی (app_voidvision_one.py)
lat = 35.82
lon = 59.91
radius = 100
from_date = "2024-08-01"
to_date = "2025-09-10"

# ✅ پوشه‌ها را ایجاد کن در صورت نبود
folders = ["outputs/geotiff", "outputs/png", "outputs/pdf", "outputs/kmz/advanced", "data"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ✅ تابع اجرا با مدیریت خطا

def run_script(desc, command):
    print(f"\n🔄 {desc}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ خطا در: {desc}")
        exit(1)
    print(f"✅ {desc} انجام شد.")

# --- مراحل تحلیل 7 فاز ---

# 1. تحلیل NDVI
run_script("تحلیل NDVI", f"python subsurface_analyze.py --lat {lat} --lon {lon} --radius {radius} --mode ndvi --from {from_date} --to {to_date}")

# 2. تحلیل NDWI
run_script("تحلیل NDWI", f"python subsurface_analyze.py --lat {lat} --lon {lon} --radius {radius} --mode ndwi --from {from_date} --to {to_date}")

# 3. تحلیل VOID
run_script("تحلیل فضای خالی (VOID)", f"python subsurface_analyze.py --lat {lat} --lon {lon} --radius {radius} --mode void --from {from_date} --to {to_date}")

# 4. ساخت Probability Map
run_script("ساخت نقشه احتمال", "python probability_map.py")

# 5. تحلیل فلزات (طلا، نقره، مس)
run_script("تحلیل فلزات", f"python metal_indices.py --lat {lat} --lon {lon} --radius {radius}")

# 6. تحلیل حرارتی (LST)
run_script("تحلیل حرارتی Landsat", "python lst_analyze.py")

# 7. ساخت گزارش PDF
from pdf_report import generate_pdf_report
from pathlib import Path

# یافتن آخرین فایل‌های خروجی

def get_latest(folder, ext):
    files = sorted([f for f in Path(folder).glob(f"*{ext}")], key=os.path.getmtime, reverse=True)
    return str(files[0]) if files else ""

pdf_path = generate_pdf_report(
    lat=lat,
    lon=lon,
    kmz_file=os.path.basename(get_latest("outputs/kmz/advanced", ".kmz")),
    png_file=os.path.basename(get_latest("outputs/png", ".png")),
    geotiff_file=os.path.basename(get_latest("outputs/geotiff", ".tif")),
    lst_file=os.path.basename(get_latest("outputs/png", "lst"))
)
print(f"✅ گزارش PDF ساخته شد: {pdf_path}")

# 8. ساخت فایل KMZ تصویری (void_fixed.png)
print("🎯 ساخت فایل KMZ برای Google Earth")
import zipfile
import shutil

img_path = Path("outputs/png/void_fixed.png")
if not img_path.exists():
    print("❌ فایل void_fixed.png یافت نشد. ساخت KMZ لغو شد.")
else:
    north, south = lat + 0.0009, lat - 0.0009
    east, west = lon + 0.0009, lon - 0.0009
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("outputs/kmz/advanced")
    kml_path = out_dir / f"void_overlay.kml"
    kml = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://www.opengis.net/kml/2.2\">
  <GroundOverlay>
    <name>Void Map</name>
    <Icon><href>{img_path.name}</href></Icon>
    <LatLonBox>
      <north>{north}</north><south>{south}</south>
      <east>{east}</east><west>{west}</west>
    </LatLonBox>
  </GroundOverlay>
</kml>"""
    kml_path.write_text(kml)
    img_copy = out_dir / img_path.name
    shutil.copy(img_path, img_copy)
    kmz_path = out_dir / f"void_overlay_{timestamp}.kmz"
    with zipfile.ZipFile(kmz_path, "w") as z:
        z.write(kml_path, arcname="doc.kml")
        z.write(img_copy, arcname=img_copy.name)
    kml_path.unlink()
    img_copy.unlink()
    print(f"✅ فایل KMZ ساخته شد: {kmz_path.name}")

print("\n🎉 اجرای کامل تحلیل VoidVision ONE به پایان رسید.")