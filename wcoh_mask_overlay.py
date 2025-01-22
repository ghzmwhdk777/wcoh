from pathlib import Path
from typing import Union
import numpy as np
import torch
from PIL import Image

def pil2tensor(image: Image.Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def tensor2pil(tensor: torch.Tensor) -> Image.Image:
    image = (tensor.squeeze(0).numpy() * 255.0).astype(np.uint8)
    return Image.fromarray(image)

class wcoh_mask_overlay:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image": ("IMAGE", ),  # 기본 이미지
                "mask_image": ("IMAGE", ),  # 오버레이할 마스크 이미지
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1}),  # 스케일 조정
                "x_padding": ("INT", {"default": 0, "min": -5000, "max": 5000, "step": 1}),  # X축 패딩
                "y_padding": ("INT", {"default": 0, "min": -5000, "max": 5000, "step": 1}),  # Y축 패딩
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("overlayed_image",)
    FUNCTION = "apply_mask_overlay"
    CATEGORY = "wcoh_korean_func/mask_overlay"

    def apply_mask_overlay(self, base_image: torch.Tensor, mask_image: torch.Tensor, scale: float, x_padding: int, y_padding: int):
        # PyTorch Tensor를 PIL 이미지로 변환
        base_pil = tensor2pil(base_image)
        mask_pil = tensor2pil(mask_image).convert("RGBA")  # 투명도를 유지

        # 마스크 이미지를 기본 이미지의 너비에 맞게 비율 유지하여 리사이즈
        base_width, base_height = base_pil.size
        mask_width, mask_height = mask_pil.size
        aspect_ratio = mask_height / mask_width

        new_mask_width = int(base_width * scale)
        new_mask_height = int(new_mask_width * aspect_ratio)
        resized_mask = mask_pil.resize((new_mask_width, new_mask_height), Image.Resampling.LANCZOS)

        # 기본 이미지에 마스크 이미지 오버레이 (좌상단 기준)
        overlay_image = base_pil.copy()
        overlay_position = (
            x_padding,  # 좌상단 X축 패딩 적용
            y_padding   # 좌상단 Y축 패딩 적용
        )
        overlay_image.paste(resized_mask, overlay_position, resized_mask)

        # 결과 이미지를 PyTorch Tensor로 변환
        return (pil2tensor(overlay_image),)

NODE_CLASS_MAPPINGS = {
    "wcoh_mask_overlay": wcoh_mask_overlay,
}
