# train_unet.py
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import ImageFolder
from unet_model import UNet
from tqdm import tqdm
from PIL import Image

# مسیر پوشه‌ها
IMAGE_DIR = "data/training/images"
MASK_DIR = "data/training/masks"
SAVE_PATH = "models/unet_model.pth"

# تنظیمات
EPOCHS = 15
BATCH_SIZE = 4
LR = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# دیتاست کاستوم
class SegmentationDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.image_names = os.listdir(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_dir, self.image_names[idx])
        mask_path = os.path.join(self.mask_dir, self.image_names[idx])
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask

# Transformations
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

# دیتاست و لودر
dataset = SegmentationDataset(IMAGE_DIR, MASK_DIR, transform)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# مدل، loss، optimizer
model = UNet(in_channels=3, out_channels=1).to(DEVICE)
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# آموزش
model.train()
for epoch in range(EPOCHS):
    loop = tqdm(loader, desc=f"Epoch {epoch+1}/{EPOCHS}")
    for images, masks in loop:
        images, masks = images.to(DEVICE), masks.to(DEVICE)
        outputs = model(images)
        loss = criterion(outputs, masks)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loop.set_postfix(loss=loss.item())

# ذخیره مدل
torch.save(model.state_dict(), SAVE_PATH)
print(f"✅ مدل ذخیره شد: {SAVE_PATH}")