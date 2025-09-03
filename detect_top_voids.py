# detect_top_voids.py
import rasterio
import numpy as np
from rasterio.transform import xy
import csv

# مسیر فایل نقشه احتمال
tif_path = "outputs/geotiff/probability_map.tif"

# باز کردن فایل
with rasterio.open(tif_path) as ds:
    arr = ds.read(1)
    transform = ds.transform

# استخراج مکان‌های با بالاترین مقدار
flat = arr.flatten()
idx_top = np.argsort(flat)[-3:][::-1]  # 3 نقطه برتر (بیشترین مقدار)
coords = [xy(transform, i // arr.shape[1], i % arr.shape[1]) for i in idx_top]
scores = flat[idx_top]

# ذخیره به CSV
csv_path = "outputs/top_voids.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Rank", "Longitude", "Latitude", "Score"])
    for i, (lon, lat) in enumerate(coords):
        writer.writerow([f"T{i+1}", lon, lat, scores[i]])

print(f"✅ Top 3 void points saved to: {csv_path}")