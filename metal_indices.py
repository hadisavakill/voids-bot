# metal_indices.py
# محاسبه شاخص‌های طلا / نقره / مس از داده‌های Sentinel-2

import os
import numpy as np
import rasterio
from rasterio.transform import from_origin
from dotenv import load_dotenv
from sentinelhub import SHConfig, BBox, CRS, DataCollection, MimeType, bbox_to_dimensions, SentinelHubRequest

load_dotenv()

# ---------- Sentinel Hub Configuration ----------
def get_config():
    cfg = SHConfig()
    cfg.sh_client_id = os.getenv("SENTINELHUB_CLIENT_ID")
    cfg.sh_client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")
    return cfg

# ---------- Bounding Box from Lat/Lon ----------
def bbox_from_center(lat, lon, radius):
    dlat = radius / 111320.0
    dlon = radius / (111320.0 * max(1e-6, np.cos(np.radians(lat))))
    return BBox([lon - dlon, lat - dlat, lon + dlon, lat + dlat], crs=CRS.WGS84)

# ---------- Evalscript ----------
evalscript_metals = """
//VERSION=3
function setup() {
  return {
    input: [{bands: ["B02", "B04", "B08", "B11"], units: "REFLECTANCE"}],
    output: {bands: 3, sampleType: "FLOAT32"}
  };
}
function evaluatePixel(s) {
  let gi = (s.B11 - s.B04) / (s.B11 + s.B04 + 1e-6);        // Gold Index
  let si = s.B11 / (s.B08 + 1e-6);                          // Silver Index
  let ci = (s.B04 - s.B11) / (s.B04 + s.B11 + 1e-6);        // Copper Index
  return [gi, si, ci];
}
"""

# ---------- Request Data from Sentinel Hub ----------
def request_metal_indices(lat, lon, radius, date_from, date_to):
    bbox = bbox_from_center(lat, lon, radius)
    size = bbox_to_dimensions(bbox, resolution=10)
    cfg = get_config()
    req = SentinelHubRequest(
        evalscript=evalscript_metals,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=(date_from, date_to)
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=cfg
    )
    return req.get_data()[0], bbox

# ---------- Save TIFFs ----------
def save_geotiffs(arr, bbox, prefix):
    height, width, _ = arr.shape
    transform = from_origin(bbox.min_x, bbox.max_y, 10, 10)
    bands = ["gold", "silver", "copper"]
    os.makedirs("outputs/geotiff", exist_ok=True)
    for i, name in enumerate(bands):
        out_path = f"outputs/geotiff/{name}_index.tif"
        with rasterio.open(out_path, "w", driver="GTiff",
            height=height, width=width, count=1,
            dtype="float32", crs="EPSG:4326", transform=transform) as dst:
            dst.write(arr[:,:,i], 1)
        print(f"[+] Saved: {out_path}")

# ---------- MAIN ----------
if __name__ == "__main__":
    lat, lon = 35.82505, 59.91487
    radius = 300
    date_from = "2024-08-01"
    date_to   = "2025-08-01"
    data, bbox = request_metal_indices(lat, lon, radius, date_from, date_to)
    save_geotiffs(data, bbox, "metals")