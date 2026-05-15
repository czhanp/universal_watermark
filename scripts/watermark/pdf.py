from __future__ import annotations

from pathlib import Path

from .common import create_watermark_layer, find_font, layer_to_png_bytes
from .options import WatermarkOptions


def watermark_pdf(input_path: Path, output_path: Path, options: WatermarkOptions) -> Path:
    try:
        import fitz
    except ImportError as e:
        raise ImportError("处理 PDF 需要安装 PyMuPDF：pip install pymupdf") from e

    font = find_font(options.font_path)
    doc = fitz.open(str(input_path))
    try:
        for page in doc:
            rect = page.rect
            width_px = max(1, int(rect.width / 72 * options.dpi))
            height_px = max(1, int(rect.height / 72 * options.dpi))
            layer = create_watermark_layer(width_px, height_px, options, font)
            png = layer_to_png_bytes(layer, options.dpi)
            page.insert_image(rect, stream=png, overlay=True, keep_proportion=False)
        doc.save(str(output_path), garbage=4, deflate=True)
    finally:
        doc.close()
    return output_path
