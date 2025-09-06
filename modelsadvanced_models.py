# models/advanced_models.py
import torch
import segmentation_models_pytorch as smp

def get_unetplusplus():
    return smp.UnetPlusPlus(encoder_name="resnet34", encoder_weights="imagenet", in_channels=3, classes=1)

def get_deeplabv3():
    return smp.DeepLabV3(encoder_name="resnet50", encoder_weights="imagenet", in_channels=3, classes=1)

def get_vit():
    from timm import create_model
    from torch import nn
    vit = create_model('vit_base_patch16_224', pretrained=True)
    vit.head = nn.Sequential(
        nn.Linear(vit.head.in_features, 512),
        nn.ReLU(),
        nn.Linear(512, 1)
    )
    return vit