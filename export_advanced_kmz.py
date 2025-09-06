# export_advanced_kmz.py

import os
import numpy as np
import rasterio
import simplekml
from rasterio.warp import transform_bounds


def normalize(arr):
    arr = np.nan_to_num(arr)
    arr = (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-6)
    return np.clip(arr, 0, 1)


def export_kmz(tif_path, kmz_path, colormap="hot", threshold=0.5):
    with rasterio.open(tif_path) as src:
        data = src.read(1).astype("float32")
        bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)

    norm = normalize(data)
    mask = norm >= threshold
    lat_min, lon_min, lat_max, lon_max = bounds[1], bounds[0], bounds[3], bounds[2]

    # ساخت KMZ
    kml = simplekml.Kml()
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j]:
                lat = lat_max - (i / mask.shape[0]) * (lat_max - lat_min)
                lon = lon_min + (j / mask.shape[1]) * (lon_max - lon_min)
                pnt = kml.newpoint(coords=[(lon, lat)])
                pnt.style.iconstyle.color = simplekml.Color.red
                pnt.style.iconstyle.scale = 0.6
                pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/target.png"

    kml.savekmz(kmz_path)
    print(f"✅ KMZ file saved: {kmz_path}")


# مثال اجرا
if __name__ == "__main__":
    tif_input = "outputs/geotiff/void_2024-08-01_35.82505_59.91487_r300.tif"
    kmz_output = "outputs/kmz/advanced/void_advanced.kmz"
    export_kmz(tif_input, kmz_output)