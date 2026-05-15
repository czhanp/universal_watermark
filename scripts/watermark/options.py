from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class WatermarkOptions:
    text: str = "棱镜极智能"
    angle: float = 45.0
    opacity: float = 0.18
    color: tuple[int, int, int] = (120, 120, 120)
    font_size_ratio: float = 0.055
    # layout 控制水印平铺方式：
    # - checkerboard：文字槽 / 空槽交错排布，下一行把文字放到上一行空槽位置
    # - staggered：旧版错行平铺
    layout: str = "checkerboard"
    spacing_x_ratio: float = 0.32
    spacing_y_ratio: float = 0.18
    spacing_y_font_multiplier: Optional[float] = 1.5
    # checkerboard 模式专用：横向空隙按字体行高的倍数计算
    spacing_x_font_multiplier: float = 0.5
    # checkerboard 模式专用：空槽宽度 = 文字槽宽度 * empty_slot_multiplier
    empty_slot_multiplier: float = 1.0
    font_path: Optional[str] = None
    suffix: str = "_加水印"
    legacy_target: str = "editable"
    excel_mode: str = "background"  # background, overlay, both
    dpi: int = 150
    jpeg_quality: int = 95
