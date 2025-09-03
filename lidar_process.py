# lidar_process.py
import os, argparse, numpy as np, rasterio

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem_old", required=True, help="DEM یا LiDAR قدیمی‌تر (مثلاً سال 2022)")
    ap.add_argument("--dem_new", required=True, help="DEM جدیدتر (مثلاً سال 2024)")
    ap.add_argument("--out_dir", default="outputs")
    ap.add_argument("--thresh", type=float, default=0.15, help="حد آستانه تغییر ارتفاع (متر)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    dso = rasterio.open(args.dem_old)
    dsn = rasterio.open(args.dem_new)
    old = dso.read(1).astype("float32")
    new = dsn.read(1).astype("float32")
    profile = dso.profile

    diff = new - old
    mask = (np.abs(diff) >= args.thresh).astype("float32")

    profile.update(dtype="float32", count=1)

    with rasterio.open(os.path.join(args.out_dir, "lidar_diff.tif"), "w", **profile) as dst:
        dst.write(diff, 1)

    with rasterio.open(os.path.join(args.out_dir, "lidar_anomaly_mask.tif"), "w", **profile) as dst:
        dst.write(mask, 1)

    print("✅ Saved:", os.path.join(args.out_dir, "lidar_diff.tif"))
    print("✅ Saved:", os.path.join(args.out_dir, "lidar_anomaly_mask.tif"))

if __name__ == "__main__":
    main()