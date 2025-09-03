# export_void_kmz.py
import os
import simplekml
import rasterio
from rasterio.plot import reshape_as_image
from PIL import Image

def export_void_to_kmz(geotiff_path, kmz_path, temp_png="temp_void.png"):
    with rasterio.open(geotiff_path) as src:
        arr = src.read(1)
        bounds = src.bounds

    # نرمال‌سازی تصویر برای نمایش بهتر
    arr_norm = ((arr - arr.min()) / (arr.max() - arr.min() + 1e-6) * 255).astype("uint8")
    img = Image.fromarray(arr_norm)
    img_path = temp_png
    img.save(img_path)

    # ساخت KMZ
    kml = simplekml.Kml()
    ground = kml.newgroundoverlay(name="Void Probability")
    ground.icon.href = img_path
    ground.latlonbox.north = bounds.top
    ground.latlonbox.south = bounds.bottom
    ground.latlonbox.east  = bounds.right
    ground.latlonbox.west  = bounds.left
    kml.savekmz(kmz_path)

    print("✅ Void KMZ saved to:", kmz_path)

# اجرای مستقیم
export_void_to_kmz("outputs/geotiff/probability_map.tif", "outputs/geotiff/probability_map.kmz")