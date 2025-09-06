# فایل: vv_metal_indices.py – تحلیل شاخص‌های فلزی (طلا، نقره، مس)

import os
import sys
import argparse
from datetime import datetime
from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, MimeType, DataCollection, bbox_to_dimensions
from PIL import Image
import numpy as np
from pathlib import Path
import rasterio

# دریافت کلیدهای Sentinel Hub
config = SHConfig()
config.sh_client_id = os.getenv("SH_CLIENT_ID")
config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

if not config.sh_client_id or not config.sh_client_secret:
    print("❌ کلیدهای Sentinel Hub تنظیم نشده‌اند.")
    sys.exit(1)

# پارامترها
parser = argparse.ArgumentParser()
parser.add_argument("--lat", type=float, required=True)
parser.add_argument("--lon", type=float, required=True)
parser.add_argument("--radius", type=int, default=100)
args = parser.parse_args()

lat, lon = args.lat, args.lon
radius = args.radius
from_date = "2024-08-01"
to_date = datetime.today().strftime("%Y-%m-%d")

meters_per_degree = 111_000
delta = radius / meters_per_degree
bbox = BBox([lon - delta, lat - delta, lon + delta, lat + delta], crs=CRS.WGS84)
dim = bbox_to_dimensions(bbox, resolution=10)

# تعریف شاخص‌ها
indices = {
    "gold": "(B11 - B04) / (B11 + B04)",
    "copper": "(B11 - B12) / (B11 + B12)",
    "silver": "(B08 - B11) / (B08 + B11)"
}

for metal, formula in indices.items():
    print(f"🧲 در حال تحلیل {metal.upper()}...")

    evalscript = f"""
    //VERSION=3
    function setup() {{ return {{ input: ["B02", "B03", "B04", "B08", "B11", "B12"], output: {{ bands: 1 }} }}; }}
    function evaluatePixel(s) {{ return [{formula}]; }}
    """

    request = SentinelHubRequest(
        evalscript=evalscript,
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

    data = request.get_data()[0].squeeze()
    scaled = ((data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data)) * 255).astype(np.uint8)
    img = Image.fromarray(np.stack([scaled]*3, axis=-1))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_png = Path("outputs/png")