from pathlib import Path
from typing import Union
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

def pil2tensor(image: Image.Image) -> torch.Tensor:
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def tensor2pil(tensor: torch.Tensor) -> Image.Image:
    image = (tensor.squeeze(0).numpy() * 255).astype(np.uint8)
    return Image.fromarray(image)

class wcoh_text_on_image_team_name:
    fonts = {}

    def __init__(self):
        pass

    @classmethod
    def CACHE_FONTS(cls):
        font_extensions = ["*.ttf", "*.otf", "*.woff", "*.woff2", "*.eot"]
        fonts = []
        for extension in font_extensions:
            fonts.extend(Path(".").glob(f"**/{extension}"))
        for font in fonts:
            cls.fonts[font.stem] = font.as_posix()
        # 기본 한글 지원 글꼴 설정
        default_font_path = "/root/app/custom_nodes/wcoh/Jalnan2TTF.ttf"  # 시스템에 설치된 한글 글꼴 경로
        if Path(default_font_path).exists():
            cls.fonts["Jalnan2TTF"] = default_font_path

    @classmethod
    def INPUT_TYPES(cls):
        if not cls.fonts:
            cls.CACHE_FONTS()
        default_font = "Jalnan2TTF" if "Jalnan2TTF" in cls.fonts else next(iter(cls.fonts.keys()), "")
        return {
            "required": {
                "image": ("IMAGE", ),  # 입력 이미지
                "text": ("STRING", {"default": "유플러스에서 힘찬 도약을 응원합니다."}),  # 추가할 텍스트
                "selected_font": ((sorted(cls.fonts.keys())), {"default": default_font}),  # 선택 가능한 폰트
                "font_size": ("INT", {"default": 40, "min": 10, "max": 200, "step": 1}),  # 글씨 크기
                "color": ("COLOR", {"default": "white"}),  # 텍스트 색상
                "shadow_color": ("COLOR", {"default": "black"}),  # 그림자 색상
                "shadow_offset_x": ("INT", {"default": 2, "min": -100, "max": 100, "step": 1}),  # 그림자 X 오프셋
                "shadow_offset_y": ("INT", {"default": 2, "min": -100, "max": 100, "step": 1}),  # 그림자 Y 오프셋
                "alignment": ([ "LEFT", "CENTER", "RIGHT" ], {"default": "CENTER"}),  # X축 정렬
                "position_y": ("INT", {"default": 50, "min": 0, "max": 5000, "step": 1}),  # Y 좌표
                "x_padding": ("INT", {"default": 5, "min": -5000, "max": 5000, "step": 1}),  # X축 패딩
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_with_text",)
    FUNCTION = "add_text_to_image"
    CATEGORY = "wcoh_korean_func/text_on_image"

    def add_text_to_image(self, image: torch.Tensor, text: str, selected_font: str, font_size: int, color: str,
                          shadow_color: str, shadow_offset_x: int, shadow_offset_y: int,
                          alignment: str, position_y: int, x_padding: int):
        # PyTorch Tensor를 PIL 이미지로 변환
        pil_image = tensor2pil(image)
        draw = ImageDraw.Draw(pil_image)

        # 선택된 폰트 로드
        font_path = self.fonts.get(selected_font, self.fonts.get("LG_Smart_UI-SemiBold"))
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        # 텍스트 크기 계산
        text_bbox = font.getbbox(text)  # (left, top, right, bottom)
        text_width = text_bbox[2] - text_bbox[0]

        # X 위치 계산
        image_width, _ = pil_image.size
        if alignment == "LEFT":
            position_x = x_padding
        elif alignment == "CENTER":
            position_x = (image_width - text_width) // 2 + x_padding
        elif alignment == "RIGHT":
            position_x = image_width - text_width - x_padding
        else:
            position_x = x_padding  # 기본값은 LEFT로 처리

        # 그림자 추가
        shadow_position = (position_x + shadow_offset_x, position_y + shadow_offset_y)
        draw.text(shadow_position, text, fill=shadow_color, font=font)

        # 텍스트 추가
        draw.text((position_x, position_y), text, fill=color, font=font)

        # PIL 이미지를 PyTorch Tensor로 변환
        return (pil2tensor(pil_image),)

NODE_CLASS_MAPPINGS = {
    "wcoh_text_on_image_team_name": wcoh_text_on_image_team_name,
}
