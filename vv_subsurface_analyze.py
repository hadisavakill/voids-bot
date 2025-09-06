# فایل: vv_subsurface_analyze.py – نسخه نهایی تحلیل NDVI / NDWI / VOID

import os
import sys
import argparse
from datetime import datetime
from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, MimeType, DataCollection, bbox_to_dimensions
from PIL import Image
import numpy as np
from pathlib import Path
import rasterio

# تنظیمات API
config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

# بررسی کلیدهای محیطی
if not config.sh_client_id or not config.sh_client_secret:
    print("❌ خطا: لطفاً کلیدهای Sentinel Hub را در فایل .env یا محیط تنظیم کنید.")
    sys.exit(1)

# پارامترهای ورودی
parser = argparse.ArgumentParser()
parser.add_argument("--lat", type=float, required=True)
parser.add_argument("--lon", type=float, required=True)
parser.add_argument("--radius", type=int, default=100)
parser.add_argument("--mode", type=str, choices=["ndvi", "ndwi", "void"], required=True)
parser.add_argument("--from", dest="from_date", type=str, required=True)
parser.add_argument("--to", dest="to_date", type=str, required=True)
args = parser.parse_args()

lat, lon = args.lat, args.lon
radius = args.radius
from_date = args.from_date
to_date = args.to_date
mode = args.mode

# محاسبه محدوده تصویر
meters_per_degree = 111_000
side_deg = radius / meters_per_degree
bbox = BBox([lon - side_deg, lat - side_deg, lon + side_deg, lat + side_deg], crs=CRS.WGS84)
dim = bbox_to_dimensions(bbox, resolution=10)

# تعریف evalscriptها
evalscripts = {
    "ndvi": """
    // NDVI
    return [
      (B08 - B04) / (B08 + B04)
    ];
    """,
    "ndwi": """
    // NDWI
    return [
      (B03 - B08) / (B03 + B08)
    ];
    """,
    "void": """
    // شاخص فضای خالی با ترکیب NDVI و NDWI معکوس
    let ndvi = (B08 - B04) / (B08 + B04);
    let ndwi = (B03 - B08) / (B03 + B08);
    return [1.0 - (ndvi + ndwi)/2.0];
    """
}

# تعریف درخواست
request = SentinelHubRequest(
    evalscript=f"""
    //VERSION=3
    function setup() {{ return {{ input: ["B02", "B03", "B04", "B08"], output: {{ bands: 1 }} }}; }}
    function evaluatePixel(sample) {{ return [{evalscripts[mode]}]; }}
    """,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=(from_date, to_date),
            mosaicking_order="mostRecent"
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=dim,
    config=config
)

img = request.get_data()[0].squeeze()

# ذخیره به‌صورت تصویر PNG
img_scaled = ((img - np.nanmin(img)) / (np.nanmax(img) - np.nanmin(img)) * 255).astype(np.uint8)
img_rgb = np.stack([img_scaled]*3, axis=-1)
img_pil = Image.fromarray(img_rgb)
output_folder = Path("outputs/png")
output_folder.mkdir(exist_ok=True, parents=True)
name = f"{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
img_pil.save(output_folder / f"{name}.png")

# ذخیره به‌صورت GeoTIFF
output_geo = Path("outputs/geotiff") / f"{name}.tif"
with rasterio.open(
    output_geo, "w",
    driver="GTiff",
    height=img.shape[0],
    width=img.shape[1],
    count=1,
    dtype=img.dtype,
    crs="EPSG:4326",
    transform=rasterio.transform.from_bounds(*bbox, img.shape[1], img.shape[0])
) as dst:
    dst.write(img, 1)

print(f"✅ {mode.upper()} ذخیره شد: {name}")