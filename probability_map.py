import rasterio
import numpy as np
import os

# 🔹 مسیر فایل‌های GeoTIFF — نام‌ها را بر اساس خروجی واقعی تنظیم کن
ndvi_path = "outputs/geotiff/ndvi_20250902_153025.tif"
ndwi_path = "outputs/geotiff/ndwi_20250902_153030.tif"
void_path = "outputs/geotiff/void_20250902_153034.tif"

# 🔸 فقط جهت بررسی: چاپ مسیرها
print("\n🗂️ Using files:")
print("   NDVI:", ndvi_path)
print("   NDWI:", ndwi_path)
print("   VOID:", void_path)

# 🟩 بارگذاری NDVI
with rasterio.open(ndvi_path) as ds:
    ndvi = ds.read(1).astype("float32")
    profile = ds.profile

# 🟦 بارگذاری NDWI
with rasterio.open(ndwi_path) as ds:
    ndwi = ds.read(1).astype("float32")

# 🟫 بارگذاری VOID
with rasterio.open(void_path) as ds:
    void = ds.read(1).astype("float32")

# ⚠️ بررسی ابعاد فایل‌ها (اختیاری)
if not (ndvi.shape == ndwi.shape == void.shape):
    raise ValueError(f"Shapes not aligned: NDVI {ndvi.shape}, NDWI {ndwi.shape}, VOID {void.shape}")

# 🧠 محاسبه نقشه احتمال (وزن‌دهی)
prob = 0.40 * (ndvi < 0.20).astype("float32") + \
       0.30 * (ndwi < 0.00).astype("float32") + \
       0.30 * void

# ⛔ محدودسازی بین ۰ تا ۱
prob = np.clip(prob, 0, 1).astype("float32")

# 💾 ذخیره به عنوان probability_map.tif
profile.update(dtype="float32", count=1)
out_path = "outputs/geotiff/probability_map.tif"

with rasterio.open(out_path, "w", **profile) as dst:
    dst.write(prob, 1)

print(f"\n✅ Probability Map saved to {out_path}")