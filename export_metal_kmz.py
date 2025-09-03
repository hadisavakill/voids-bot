# export_metal_kmz.py
import os
import simplekml
import rasterio

def export_to_kmz(geotiff_path, kmz_path, temp_png="temp_metal.png"):
    with rasterio.open(geotiff_path) as src:
        bounds = src.bounds

    # تبدیل GeoTIFF به PNG با GDAL
    img_path = geotiff_path.replace(".tif", ".png")
    os.system(f"gdal_translate -of PNG {geotiff_path} {img_path}")

    # ساخت فایل KMZ
    kml = simplekml.Kml()
    ground = kml.newgroundoverlay(name=os.path.basename(kmz_path))
    ground.icon.href = img_path
    ground.latlonbox.north = bounds.top
    ground.latlonbox.south = bounds.bottom
    ground.latlonbox.east  = bounds.right
    ground.latlonbox.west  = bounds.left
    kml.savekmz(kmz_path)
    print("✅ Metal KMZ saved to:", kmz_path)

# نمونه اجرا برای طلا، نقره و مس
export_to_kmz("outputs/geotiff/gold_index.tif",   "outputs/geotiff/gold_index.kmz")
export_to_kmz("outputs/geotiff/silver_index.tif", "outputs/geotiff/silver_index.kmz")
export_to_kmz("outputs/geotiff/copper_index.tif", "outputs/geotiff/copper_index.kmz")