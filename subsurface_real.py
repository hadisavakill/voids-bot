# --- subsurface_real.py (stable RGB from Sentinel Hub Process API) ---
import os
import math
import time
import json
import argparse
import requests
from dotenv import load_dotenv

# -----------------------
# 0) Read credentials
# -----------------------
load_dotenv()
CID = os.getenv("SENTINELHUB_CLIENT_ID")
CSEC = os.getenv("SENTINELHUB_CLIENT_SECRET")

TOKEN_URL   = "https://services.sentinel-hub.com/oauth/token"
PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"

# -----------------------
# Token with small retry
# -----------------------
def get_token(cid: str, csec: str) -> str:
    if not cid or not csec:
        raise RuntimeError("Set SENTINELHUB_CLIENT_ID and SENTINELHUB_CLIENT_SECRET in .env")
    last = None
    for i in range(3):
        try:
            resp = requests.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(cid, csec),
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["access_token"]
        except requests.RequestException as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

# -----------------------
# BBOX from center/radius
# -----------------------
def bbox_from_center(lat: float, lon: float, radius_m: int) -> list:
    dlat = radius_m / 111320.0
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    return [lon - dlon, lat - dlat, lon + dlon, lat + dlat]  # [minX, minY, maxX, maxY]

# -----------------------
# Simple RGB evalscript
# -----------------------
EVALSCRIPT_RGB = """//VERSION=3
function setup() {
  return { input: ["B04","B03","B02"], output: { bands: 3, sampleType: "AUTO" } };
}
function evaluatePixel(s) {
  return [s.B04, s.B03, s.B02];
}
"""

# -----------------------
# Process API request
# -----------------------
def process_image(
    token: str,
    bbox: list,
    tfrom: str,
    tto: str,
    *,
    width: int = 512,
    height: int = 512,
    use_geometry: bool = False,
    lon: float | None = None,
    lat: float | None = None,
) -> bytes:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    tfrom_iso = f"{tfrom}T00:00:00Z"
    tto_iso   = f"{tto}T23:59:59Z"

    if use_geometry and (lon is not None) and (lat is not None):
        bounds = {
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
        }
    else:
        bounds = {
            "bbox": bbox,
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
        }

    payload = {
        "input": {
            "bounds": bounds,
            "data": [
                {
                    "type": "S2L2A",
                    "dataFilter": {
                        "timeRange": {"from": tfrom_iso, "to": tto_iso},
                        "mosaickingOrder": "mostRecent",
                    },
                    "processing": {
                        "upsampling": "BILINEAR",
                        "downsampling": "BILINEAR",
                    },
                }
            ],
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": "image/png"}  # NOTE: MUST be "image/png" (object), not "PNG"
                }
            ],
        },
        "evalscript": EVALSCRIPT_RGB,
    }

    last = None
    for i in range(3):
        try:
            r = requests.post(PROCESS_URL, headers=headers, json=payload, timeout=60)
            try:
                r.raise_for_status()
                return r.content
            except requests.HTTPError:
                # Print server message to help debugging
                print("=== Server reply (debug) ===")
                try:
                    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
                except Exception:
                    print(r.text[:800])
                raise
        except requests.RequestException as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

# -----------------------
# Main CLI
# -----------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat",    type=float, required=True)
    ap.add_argument("--lon",    type=float, required=True)
    ap.add_argument("--radius", type=int,   default=300)
    ap.add_argument("--from",   dest="tfrom", required=True)  # YYYY-MM-DD
    ap.add_argument("--to",     dest="tto",   required=True)  # YYYY-MM-DD
    args = ap.parse_args()

    token = get_token(CID, CSEC)
    bbox  = bbox_from_center(args.lat, args.lon, args.radius)

    # First try with bbox (more robust). If 400, fallback to geometry point.
    try:
        img = process_image(token, bbox, args.tfrom, args.tto, width=512, height=512)
    except requests.HTTPError:
        img = process_image(
            token, bbox, args.tfrom, args.tto, width=512, height=512,
            use_geometry=True, lon=args.lon, lat=args.lat
        )

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", "s2_rgb.png")
    with open(out_path, "wb") as f:
        f.write(img)
    print("Saved:", out_path)

if __name__ == "__main__":
    main()
# --- end ---