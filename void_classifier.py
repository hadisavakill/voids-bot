# void_classifier.py
import torch
import numpy as np
import rasterio
from torchvision import transforms
from PIL import Image
from unet_model import UNet
import os

# ⚙️ تنظیمات
MODEL_PATH = "models/unet_model.pth"
INPUT_IMAGE = "inference/input.png"
OUTPUT_MASK = "outputs/ml/predicted_mask.tif"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 🔁 Transform ورودی
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# 📷 بارگذاری تصویر
img = Image.open(INPUT_IMAGE).convert("RGB")
input_tensor = transform(img).unsqueeze(0).to(DEVICE)

# 🧠 بارگذاری مدل
model = UNet(in_channels=3, out_channels=1).to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

# 🔍 پیش‌بینی
with torch.no_grad():
    output = model(input_tensor)
    pred_mask = torch.sigmoid(output).squeeze().cpu().numpy()
    binary_mask = (pred_mask > 0.5).astype("float32")

# 💾 ذخیره GeoTIFF
height, width = binary_mask.shape
transform = rasterio.transform.from_origin(0, 0, 1, 1)  # فرضی، در پروژه اصلی اصلاح شود

os.makedirs(os.path.dirname(OUTPUT_MASK), exist_ok=True)
with rasterio.open(
    OUTPUT_MASK, "w",
    driver="GTiff", height=height, width=width,
    count=1, dtype="float32",
    crs="EPSG:4326", transform=transform
) as dst:
    dst.write(binary_mask, 1)

print(f"✅ نقشه پیش‌بینی فضای خالی ذخیره شد: {OUTPUT_MASK}")