# فایل: vv_probability_map.py – ساخت نقشه احتمال (Probability Map)

import os
import numpy as np
from PIL import Image
from datetime import datetime
from pathlib import Path
import rasterio

# مسیر فایل‌ها
geotiff_dir = Path("outputs/geotiff")
png_dir = Path("outputs/png")
png_dir.mkdir(exist_ok=True, parents=True)

# یافتن جدیدترین فایل از هر شاخص

def get_latest(prefix):
    files = [f for f in geotiff_dir.glob(f"{prefix}_*.tif")]
    return sorted(files, key=os.path.getmtime, reverse=True)[0] if files else None

ndvi = get_latest("ndvi")
ndwi = get_latest("ndwi")
void = get_latest("void")

if not all([ndvi, ndwi, void]):
    print("❌ یکی از فایل‌های NDVI/NDWI/VOID یافت نشد.")
    exit(1)

# خواندن فایل‌ها
with rasterio.open(ndvi) as s1:
    a = s1.read(1)
with rasterio.open(ndwi) as s2:
    b = s2.read(1)
with rasterio.open(void) as s3:
    c = s3.read(1)

# ترکیب وزن‌دار شاخص‌ها
result = 0.3 * (1 - a) + 0.3 * (1 - b) + 0.4 * c
result = np.clip(result, 0, 1)

# ساخت تصویر رنگی Heatmap
scaled = (result * 255).astype(np.uint8)
heat = np.stack([scaled, np.zeros_like(scaled), 255 - scaled], axis=-1)
img = Image.fromarray(heat)
name = f"probability_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
img.save(png_dir / f"{name}.png")

print(f"✅ Probability Map ساخته شد: {name}.png")