import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

os.makedirs("data", exist_ok=True)  # ساخت پوشه data اگر وجود نداشته باشد

arr = np.random.rand(100, 100).astype("float32") * 100  # ارتفاع فرضی

profile = {
    "driver": "GTiff",
    "height": arr.shape[0],
    "width": arr.shape[1],
    "count": 1,
    "dtype": "float32",
    "crs": "EPSG:4326",
    "transform": from_origin(59.91487, 35.82505, 0.0001, 0.0001),
}

with rasterio.open("data/dem_2022.tif", "w", **profile) as dst:
    dst.write(arr, 1)

with rasterio.open("data/dem_2025.tif", "w", **profile) as dst:
    dst.write(arr + np.random.randn(100, 100), 1)

print("✅ DEM files created.")