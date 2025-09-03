# subsurface_analyze.py
from __future__ import annotations
import os, math, argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import rasterio
from rasterio.transform import from_origin

from sentinelhub import (
    SHConfig, BBox, CRS, DataCollection, MimeType,
    bbox_to_dimensions, SentinelHubRequest
)

# -------- ENVIRONMENT CONFIG --------
load_dotenv()

def get_config() -> SHConfig:
    cfg = SHConfig()
    cid = os.getenv("SENTINELHUB_CLIENT_ID") or os.getenv("CLIENT_ID")
    csec = os.getenv("SENTINELHUB_CLIENT_SECRET") or os.getenv("CLIENT_SECRET")
    if not cid or not csec:
        raise RuntimeError("Missing SentinelHub credentials in .env")
    cfg.sh_client_id = cid
    cfg.sh_client_secret = csec
    cfg.max_download_attempts = 3
    return cfg

# -------- CREATE OUTPUT FOLDERS --------
def ensure_dirs():
    Path("outputs/png").mkdir(parents=True, exist_ok=True)
    Path("outputs/geotiff").mkdir(parents=True, exist_ok=True)

# -------- COORDINATES → BBOX --------
def bbox_from_center(lat: float, lon: float, radius: int) -> BBox:
    dlat = radius / 111320.0
    dlon = radius / (111320.0 * max(1e-6, math.cos(math.radians(lat))))
    return BBox([lon - dlon, lat - dlat, lon + dlon, lat + dlat], crs=CRS.WGS84)

# -------- TIMESTAMP FOR OUTPUT --------
def ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

# -------- EvalScripts --------
evalscript_ndvi_png = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: { bands: 3 }
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 1e-6);
  return [ndvi, ndvi, ndvi];
}
"""

evalscript_ndvi_tif = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04 + 1e-6)];
}
"""

evalscript_ndwi_png = """
//VERSION=3
function setup() {
  return {
    input: ["B03", "B08"],
    output: { bands: 3 }
  };
}
function evaluatePixel(sample) {
  let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08 + 1e-6);
  return [ndwi, ndwi, ndwi];
}
"""

evalscript_ndwi_tif = """
//VERSION=3
function setup() {
  return {
    input: ["B03", "B08"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  return [(sample.B03 - sample.B08) / (sample.B03 + sample.B08 + 1e-6)];
}
"""

evalscript_void_tif = """
//VERSION=3
function setup() {
  return {
    input: [{bands: ["B02","B03","B04","B08","B11"], units: "REFLECTANCE"}],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  let ndvi = (s.B08 - s.B04) / (s.B08 + s.B04 + 1e-6);
  let ndwi = (s.B03 - s.B08) / (s.B03 + s.B08 + 1e-6);
  let bsi  = ((s.B11 + s.B04) - (s.B08 + s.B02)) / ((s.B11 + s.B04) + (s.B08 + s.B02) + 1e-6);
  let score = (1 - ndvi) * 0.4 + (1 - ndwi) * 0.3 + bsi * 0.3;
  score = Math.max(0, Math.min(1, score));
  return [score];
}
"""

# -------- REQUEST MAKER --------
def make_request(evalscript, bbox, time_interval, mime, cfg):
    size = bbox_to_dimensions(bbox, resolution=10)
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=time_interval
        )],
        responses=[SentinelHubRequest.output_response("default", mime)],
        bbox=bbox, size=size, config=cfg
    )

# -------- MAIN EXECUTION --------
def run_mode(mode, lat, lon, radius, date_from, date_to):
    ensure_dirs()
    cfg = get_config()
    bbox = bbox_from_center(lat, lon, radius)
    stamp = ts()

    if mode == "ndvi":
        evalscript_png = evalscript_ndvi_png
        evalscript_tif = evalscript_ndvi_tif
    elif mode == "ndwi":
        evalscript_png = evalscript_ndwi_png
        evalscript_tif = evalscript_ndwi_tif
    elif mode == "void":
        evalscript_png = None
        evalscript_tif = evalscript_void_tif
    else:
        raise ValueError("mode must be: ndvi or ndwi or void")

    # PNG
    if evalscript_png:
        out_png = Path(f"outputs/png/{mode}_{stamp}.png")
        req_png = make_request(evalscript_png, bbox, (date_from, date_to), MimeType.PNG, cfg)
        req_png = req_png.get_data()
        with open(out_png, "wb") as f:
            f.write(req_png[0])
        print(f"[✓] {mode.upper()} PNG saved to {out_png}")

    # GeoTIFF
    out_tif = Path(f"outputs/geotiff/{mode}_{stamp}.tif")
    req_tif = make_request(evalscript_tif, bbox, (date_from, date_to), MimeType.TIFF, cfg)
    data = req_tif.get_data()[0]

    if data is not None:
        height, width = data.shape
        transform = from_origin(bbox.min_x, bbox.max_y, 10, 10)
        with rasterio.open(
            out_tif, "w", driver="GTiff",
            height=height, width=width,
            count=1, dtype="float32", crs="EPSG:4326", transform=transform
        ) as dst:
            dst.write(data, 1)
        print(f"[✓] {mode.upper()} GeoTIFF saved to {out_tif}")
    else:
        print(f"[X] {mode.upper()} GeoTIFF not saved – no data received.")

# -------- ENTRY POINT --------
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Robat Vahed – S2 NDVI/NDWI/Void")
    p.add_argument("--mode", choices=["ndvi","ndwi","void"], required=True)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--radius", type=int, default=300)
    p.add_argument("--from", dest="date_from", required=True)
    p.add_argument("--to", dest="date_to", required=True)
    args = p.parse_args()
    run_mode(args.mode, args.lat, args.lon, args.radius, args.date_from, args.date_to)