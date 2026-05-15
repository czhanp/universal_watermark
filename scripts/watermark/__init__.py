"""Universal watermark package.

入口：
    python scripts/universal_watermark.py input.docx --text "棱镜极智能"
"""

from .options import WatermarkOptions
from .dispatcher import watermark_file

__all__ = ["WatermarkOptions", "watermark_file"]

