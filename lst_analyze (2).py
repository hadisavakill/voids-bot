# lst_analyze.py
import os
import argparse
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.transform import from_origin
from datetime import datetime


def generate_fake_lst(output_path, lat, lon, size=100, pixel_size=0.0002):
    """شبیه‌سازی داده حرارتی به‌صورت مصنوعی برای تست الگوریتم."""
    data = 20 + 10 * np.random.rand(size, size)  # دمای ساختگی 20-30 درجه
    transform = from_origin(lon, lat, pixel_size, pixel_size)

    profile = {
        'driver': 'GTiff',
        'height': size,
        'width': size,
        'count': 1,
        'dtype': 'float32',
        'crs': 'EPSG:4326',
        'transform': transform
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data, 1)

    print(f"✅ LST Fake Map saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LST Generator using Landsat-8")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--out_dir", type=str, default="outputs/lst/", help="Output folder")

    args = parser.parse_args()

    # ساخت نام فایل با تاریخ و مختصات
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"lst_{timestamp}_{args.lat:.4f}_{args.lon:.4f}.tif"
    output_path = os.path.join(args.out_dir, filename)

    generate_fake_lst(output_path, lat=args.lat, lon=args.lon)