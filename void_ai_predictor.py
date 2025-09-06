# فایل: void_ai_predictor.py – مدل هوش مصنوعی نهایی VoidVision X ∞

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np

# ========================
# 🧠 UNet++ سفارشی‌شده
# ========================

class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class UNetPlusPlus(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super(UNetPlusPlus, self).__init__()
        self.conv1 = DoubleConv(n_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.conv3 = DoubleConv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.final = nn.Conv2d(64, n_classes, 1)

    def forward(self, x):
        x1 = self.conv1(x)
        x2 = self.conv2(self.pool1(x1))
        x3 = self.conv3(self.pool2(x2))
        x = self.up1(x3)
        x = self.up2(x + x1)
        x = self.final(x)
        return torch.sigmoid(x)

# ========================
# 📥 بارگذاری تصویر و پیش‌پردازش
# ========================

def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB").resize((256, 256))
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5]*3, std=[0.5]*3)
    ])
    return transform(img).unsqueeze(0)  # (1, 3, 256, 256)

# ========================
# 🔮 پیش‌بینی و خروجی ماسک
# ========================

def predict_void_area(model_path, image_path, threshold=0.5):
    model = UNetPlusPlus()
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    x = preprocess_image(image_path)
    with torch.no_grad():
        output = model(x)
        mask = (output.squeeze().numpy() > threshold).astype(np.uint8) * 255
        return Image.fromarray(mask)

# ========================
# 🧪 تست سریع (در صورت نیاز)
# ========================

if __name__ == "__main__":
    test_img = "outputs/png/void_fixed.png"
    model_file = "models/void_unet_model.pth"

    if not torch.cuda.is_available():
        print("⚠️ CUDA در دسترس نیست. اجرا روی CPU.")

    if not (os.path.exists(test_img) and os.path.exists(model_file)):
        print("❌ تصویر یا مدل پیدا نشد.")
    else:
        mask_img = predict_void_area(model_file, test_img)
        mask_img.save("outputs/png/predicted_void_mask.png")
        print("✅ پیش‌بینی ناحیه فضای خالی انجام شد و ذخیره شد.")