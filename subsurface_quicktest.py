import argparse 
import os
import numpy as np
import rasterio
from rasterio.io import MemoryFile
from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--radius", type=int, default=300)
    ap.add_argument("--from", dest="tfrom", required=True)
    ap.add_argument("--to", dest="tto", required=True)
    a = ap.parse_args()

    os.makedirs("outputs", exist_ok=True)

    arr = np.random.rand(100, 100).astype("float32")
    prob = np.clip(arr, 0, 1)

    Image.fromarray((prob * 255).astype("uint8")).save("outputs/probability.png")
    with rasterio.open(
        "outputs/probability.tif",
        "w",
        driver="GTiff",
        height=prob.shape[0],
        width=prob.shape[1],
        count=1,
        dtype="float32",
    ) as dst:
        dst.write(prob, 1)

    print("Done -> outputs/probability.png / probability.tif")

if __name__ == "__main__":
    main()