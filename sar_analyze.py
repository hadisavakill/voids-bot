# sar_analyze.py
import os
import numpy as np
import rasterio
from sentinelhub import SHConfig, BBox, CRS, DataCollection, MimeType, SentinelHubRequest, bbox_to_dimensions
from dotenv import load_dotenv

load_dotenv()


def get_config():
    config = SHConfig()
    config.sh_client_id = os.getenv("SENTINELHUB_CLIENT_ID")
    config.sh_client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")
    if not config.sh_client_id or not config.sh_client_secret:
        raise ValueError("Missing SentinelHub credentials.")
    return config


def get_bbox(lat, lon, radius):
    dlat = radius / 111320
    dlon = radius / (40075000 * np.cos(np.radians(lat)) / 360)
    return BBox(bbox=[lon - dlon, lat - dlat, lon + dlon, lat + dlat], crs=CRS.WGS84)


def make_sar_request(bbox, time_interval, config):
    size = bbox_to_dimensions(bbox, resolution=10)
    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["VV", "VH"],
        output: { bands: 2, sampleType: "FLOAT32" }
      };
    }
    function evaluatePixel(s) {
      return [s.VV, s.VH];
    }
    """
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1_IW,
            time_interval=time_interval,
            mosaicking_order='mostRecent'
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config
    )


def save_sar_data(lat, lon, radius, date_from, date_to):
    config = get_config()
    bbox = get_bbox(lat, lon, radius)
    request = make_sar_request(bbox, (date_from, date_to), config)
    data = request.get_data()[0]

    out_path = f"outputs/sar/sar_{lat:.5f}_{lon:.5f}.tif"
    height, width = data.shape[1:]
    transform = rasterio.transform.from_origin(bbox.min_x, bbox.max_y, 10, 10)

    with rasterio.open(out_path, "w", driver="GTiff", height=height, width=width,
                       count=2, dtype="float32", crs="EPSG:4326", transform=transform) as dst:
        dst.write(data)

    print(f"✅ SAR image saved to {out_path}")


# مثال اجرا
if __name__ == "__main__":
    save_sar_data(35.82505, 59.91487, 300, "2024-08-01", "2024-08-10")