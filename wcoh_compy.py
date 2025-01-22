from pathlib import Path
from typing import cast, Union
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import math

here = Path(__file__).parent.absolute()
comfy_dir = here.parent.parent

def pil2tensor(image: Union[Image.Image, list[Image.Image]]) -> torch.Tensor:
    if isinstance(image, list):
        return torch.cat([pil2tensor(img) for img in image], dim=0)
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def bbox_dim(bbox):
    left, upper, right, lower = bbox
    width = right - left
    height = lower - upper
    return width, height

class wcoh:

    fonts = {}

    def __init__(self):
        pass

    @classmethod
    def CACHE_FONTS(cls):
        font_extensions = ["*.ttf", "*.otf", "*.woff", "*.woff2", "*.eot"]
        fonts = []
        for extension in font_extensions:
            fonts.extend(comfy_dir.glob(f"**/{extension}"))
        for font in fonts:
            cls.fonts[font.stem] = font.as_posix()
        # 기본 한글 지원 글꼴 설정
        default_font_path = "C:/Users/user/AppData/Local/Microsoft/Windows/Fonts/Jalnan2TTF.ttf"  # 시스템에 설치된 한글 글꼴 경로
        if Path(default_font_path).exists():
            cls.fonts["Jalnan2TTF"] = default_font_path

    @classmethod
    def INPUT_TYPES(cls):
        if not cls.fonts:
            cls.CACHE_FONTS()
        default_font = "Jalnan2TTF" if "Jalnan2TTF" in cls.fonts else next(iter(cls.fonts.keys()), "")
        return {
            "required": {
                "text": ("STRING", {"default": "LG 유플러스"}),
                "selected_font": ((sorted(cls.fonts.keys())), {"default": default_font}),
                "align": (["left", "center", "right"], {"default": "center"}),
                "wrap": ("INT", {"default": 0, "min": 0, "max": 8096, "step": 1}),
                "font_size": ("INT", {"default": 200, "min": 1, "max": 2500, "step": 1}),
                "color": ("COLOR", {"default": "red"}),
                "outline_size": ("INT", {"default": 0, "min": 0, "max": 8096, "step": 1}),
                "outline_color": ("COLOR", {"default": "blue"}),
                "margin_x": ("INT", {"default": 0, "min": 0, "max": 8096, "step": 1}),
                "margin_y": ("INT", {"default": 0, "min": 0, "max": 8096, "step": 1}),
                "line_spacing": ("INT", {"default": 10, "min": 0, "max": 8096, "step": 1}),
                "width": ("INT", {"default": 1024, "min": 1, "max": 8096, "step": 1}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 8096, "step": 1}),
                "swap": ("BOOLEAN", {"default": False}),
                "arc_text": ("BOOLEAN", {"default": False}),
                "arc_radius": ("INT", {"default": 100, "min": 1, "max": 2500, "step": 1}),
                "arc_start_angle": ("INT", {"default": 180, "min": 0, "max": 360, "step": 1}),
                "arc_end_angle": ("INT", {"default": 360, "min": 0, "max": 360, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "text_to_image"
    CATEGORY = "wcoh_korean_func/text"

    def draw_text_in_arc(self, image, draw, text, font, font_path, font_size, center, radius, start_angle, end_angle, fill='black', stroke_fill='blue', stroke_width=0):
        text_width = sum(font.getbbox(char)[2] - font.getbbox(char)[0] for char in text[:-1])
        angle_range = end_angle - start_angle
        angle_step = (angle_range / (len(text) - 1) if len(text) > 1 else 1)
        current_angle = start_angle
        for char in text:
            char_bbox = font.getbbox(char)
            char_width = char_bbox[2] - char_bbox[0]
            char_height = char_bbox[3] - char_bbox[1]
            angle = math.radians(current_angle)
            super_sampling_multiplier = 10
            char_image = Image.new("RGBA", (char_width * super_sampling_multiplier, char_height * super_sampling_multiplier), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_image)
            super_sampling_font = cast(ImageFont.FreeTypeFont, ImageFont.truetype(font_path, font_size * super_sampling_multiplier))
            char_draw.text((0, 0), char, font=super_sampling_font, fill=fill, stroke_fill=stroke_fill, stroke_width=stroke_width)
            rotate_angle = current_angle - 90  # 수정된 각도 계산
            rotated_char_image = char_image.rotate(rotate_angle, expand=1, resample=Image.Resampling.BICUBIC)
            new_size = (int(rotated_char_image.width / 10), int(rotated_char_image.height / 10))
            rotated_char_image_resized = rotated_char_image.resize(new_size, resample=Image.Resampling.BICUBIC)
            x = center[0] + radius * math.cos(angle) - rotated_char_image_resized.size[0] / 2
            y = center[1] + radius * math.sin(angle) - rotated_char_image_resized.size[1] / 2
            image.paste(rotated_char_image_resized, (int(x), int(y)), rotated_char_image_resized)
            current_angle += angle_step

    def text_to_image(self, text, selected_font, align, wrap, font_size, width, height, color, outline_size, outline_color, margin_x, margin_y, line_spacing, swap=False, arc_text=False, arc_radius=100, arc_start_angle=180, arc_end_angle=360):
        import textwrap
        if swap:
            width, height = height, width
        font_path = self.fonts.get(selected_font, self.fonts.get("Jalnan2TTF"))
        font = cast(ImageFont.FreeTypeFont, ImageFont.truetype(font_path, font_size))
        if wrap == 0:
            wrap = width / font_size
        wrap = int(wrap)
        lines = textwrap.wrap(text, width=wrap)
        line_height = bbox_dim(font.getbbox("hg"))[1] + line_spacing
        img_height = height
        img_width = width
        img = Image.new("RGBA", (img_width, img_height), "blue")  # 배경을 blue로 설정
        draw = ImageDraw.Draw(img)
        if arc_text:
            width, height = bbox_dim(font.getbbox(text))
            center_x = (img_width) // 2
            center_y = arc_radius + (height)
            if align == "left":
                center_x = arc_radius + (height) // 2
            elif align == "right":
                center_x = img_width - arc_radius - (height) // 2
            center = (center_x + margin_x, center_y + margin_y)
            self.draw_text_in_arc(img, draw, text, font, font_path, font_size, center, arc_radius, arc_start_angle, arc_end_angle, fill=color, stroke_fill=outline_color, stroke_width=outline_size)
        else:
            y_text = margin_y + outline_size
            for line in lines:
                width, height = bbox_dim(font.getbbox(line))
                if align == "left":
                    x_text = margin_x
                elif align == "center":
                    x_text = (img_width - width) // 2
                elif align == "right":
                    x_text = img_width - width - margin_x
                else:
                    x_text = margin_x
                draw.text((x_text, y_text), text=line, fill="red", stroke_fill=outline_color, stroke_width=outline_size, font=font)  # 글씨 색을 red로 설정
                y_text += height + line_spacing
        return (pil2tensor(img),)

NODE_CLASS_MAPPINGS = {
    "wcoh": wcoh,
}
