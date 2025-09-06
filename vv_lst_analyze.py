# فایل: vv_lst_analyze.py – تحلیل LST حرارتی از Landsat TIRS

import os
import sys
import numpy as np
import rasterio
from rasterio.plot import reshape_as_image
from datetime import datetime
from pathlib import Path
from PIL import Image

# ورودی‌ها (در این نسخه برای تست مستقیم)
lat, lon = 35.82, 59.91
radius = 100

# پوشه دیتا حرارتی آماده‌سازی‌شده (فرض می‌کنیم Landsat TIRS قبلاً بارگیری شده)
source_path = Path("data/thermal/landsat_sample.tif")

if not source_path.exists():
    print("❌ فایل حرارتی Landsat یافت نشد: data/thermal/landsat_sample.tif")
    sys.exit(1)

# خروجی
output_png = Path("outputs/png") / f"lst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
output_tif = Path("outputs/geotiff") / output_png.with_suffix(".tif").name
Path("outputs/png").mkdir(parents=True, exist_ok=True)
Path("outputs/geotiff").mkdir(parents=True, exist_ok=True)

# خواندن داده
with rasterio.open(source_path) as src:
    data = src.read(1)
    profile = src.profile
    transform = src.transform

    # نرمال‌سازی دما بین 0 تا 255 برای نمایش تصویری
    norm = ((data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data)) * 255).astype(np.uint8)
    img = Image.fromarray(norm)
    img_rgb = img.convert("RGB")
    img_rgb.save(output_png)

    # ذخیره نسخه GeoTIFF
    with rasterio.open(
        output_tif, "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform
    ) as dst:
        dst.write(data, 1)

print(f"✅ تحلیل LST انجام شد → {output_png.name}")