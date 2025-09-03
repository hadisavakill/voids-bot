# export_kmz.py
import rasterio
import numpy as np
from rasterio.plot import reshape_as_image
from rasterio.warp import transform_bounds
from simplekml import Kml, OverlayXY, ScreenXY, Units
import os

# مسیر فایل GeoTIFF نهایی
tif_path = "outputs/geotiff/probability_map.tif"
kmz_output = "outputs/geotiff/probability_map.kmz"

# باز کردن فایل
with rasterio.open(tif_path) as src:
    data = src.read(1)
    profile = src.profile
    bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds)

# نرمال‌سازی تصویر به 0–255
norm = np.clip(data, 0, 1)
img = (norm * 255).astype(np.uint8)
img_rgb = np.stack([img]*3, axis=-1)  # سه کاناله RGB

# ذخیره به PNG موقت
from PIL import Image
temp_png = "outputs/geotiff/probability_temp.png"
Image.fromarray(img_rgb).save(temp_png)

# ساخت KMZ با SimpleKML
kml = Kml()
ground = kml.newgroundoverlay(name="Probability Map")
ground.icon.href = os.path.basename(temp_png)
ground.latlonbox.north = bounds[3]
ground.latlonbox.south = bounds[1]
ground.latlonbox.east = bounds[2]
ground.latlonbox.west = bounds[0]
ground.color = '80ffffff'  # شفافیت

kml.savekmz(kmz_output)

print(f"✅ KMZ exported to {kmz_output}")