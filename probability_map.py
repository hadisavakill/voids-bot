import os
import glob
import numpy as np
import rasterio
from PIL import Image

# پیدا کردن جدیدترین فایل بر اساس تاریخ ساخت
def get_latest_file(folder, prefix):
    files = sorted(glob.glob(os.path.join(folder, f"{prefix}_*.tif")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

folder = "outputs/geotiff"
ndvi_path = get_latest_file(folder, "ndvi")
ndwi_path = get_latest_file(folder, "ndwi")
void_path = get_latest_file(folder, "void")

print("🛰️ Using files:")
print("NDVI:", ndvi_path)
print("NDWI:", ndwi_path)
print("VOID:", void_path)

# بررسی فایل‌ها
if not all([ndvi_path, ndwi_path, void_path]):
    raise FileNotFoundError("❌ یکی از فایل‌های NDVI, NDWI یا VOID پیدا نشد.")

# بارگذاری داده‌ها
with rasterio.open(ndvi_path) as ds:
    ndvi = ds.read(1)
with rasterio.open(ndwi_path) as ds:
    ndwi = ds.read(1)
with rasterio.open(void_path) as ds:
    void = ds.read(1)

# نرمال‌سازی به بازه 0-255 برای ذخیره PNG
def normalize(img):
    img = np.nan_to_num(img, nan=0.0)
    min_val = np.min(img)
    max_val = np.max(img)
    if max_val - min_val == 0:
        return np.zeros_like(img, dtype=np.uint8)
    return ((img - min_val) / (max_val - min_val) * 255).astype(np.uint8)

ndvi_norm = normalize(ndvi)
ndwi_norm = normalize(ndwi)
void_norm = normalize(void)

# ذخیره تصاویر
os.makedirs("outputs/png", exist_ok=True)
Image.fromarray(ndvi_norm).save("outputs/png/ndvi_fixed.png")
Image.fromarray(ndwi_norm).save("outputs/png/ndwi_fixed.png")
Image.fromarray(void_norm).save("outputs/png/void_fixed.png")

# ساخت نقشه ترکیبی احتمال
combo = ((ndvi_norm.astype(np.float32) + ndwi_norm.astype(np.float32)) / 2 * (void_norm / 255)).astype(np.uint8)
Image.fromarray(combo).save("outputs/png/probability_map.png")

print("✅ تصاویر تحلیلی ساخته شدند.")