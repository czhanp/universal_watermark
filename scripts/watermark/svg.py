from __future__ import annotations

import tempfile
from pathlib import Path

from .image import watermark_image
from .options import WatermarkOptions


def watermark_svg_by_convert(input_path: Path, output_path: Path, options: WatermarkOptions) -> Path:
    try:
        import cairosvg
    except ImportError as e:
        raise ImportError("SVG 处理需要安装 cairosvg，或先手动转为 PNG/PDF：pip install cairosvg") from e

    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / f"{input_path.stem}.png"
        cairosvg.svg2png(url=str(input_path), write_to=str(png))
        return watermark_image(png, output_path, options)
