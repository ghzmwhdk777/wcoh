from pathlib import Path
from typing import Union
import random
import numpy as np
import torch
from PIL import Image


def pil2tensor(image: Image.Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


class wcoh_random_image:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "/root/app/custom_nodes/wcoh/winter"}),  # 폴더 경로 입력
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("random_image",)
    FUNCTION = "select_random_image"
    CATEGORY = "wcoh_korean_func/random_image"

    def select_random_image(self, folder_path: str):
        # 이미지 파일 확장자 필터링
        valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        folder = Path(folder_path)

        if not folder.is_dir():
            raise ValueError(f"'{folder_path}'는 유효한 폴더 경로가 아닙니다.")

        # 폴더 내 이미지 파일 리스트 가져오기
        image_files = [f for f in folder.iterdir() if f.suffix.lower() in valid_extensions]

        if not image_files:
            raise ValueError(f"'{folder_path}' 폴더에 이미지 파일이 없습니다.")

        # 랜덤 이미지 선택
        selected_image_path = random.choice(image_files)
        selected_image = Image.open(selected_image_path)

        return (pil2tensor(selected_image),)


NODE_CLASS_MAPPINGS = {
    "wcoh_random_image": wcoh_random_image,
}
