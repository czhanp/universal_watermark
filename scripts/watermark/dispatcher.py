from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from .constants import (
    SUPPORTED_EXCEL_LEGACY,
    SUPPORTED_EXCEL_OOXML,
    SUPPORTED_IMAGES,
    SUPPORTED_PPT_LEGACY,
    SUPPORTED_WORD_LEGACY,
)
from .converters import convert_with_libreoffice
from .detector import detect_file_type
from .excel import watermark_xlsx
from .gif import watermark_gif
from .image import watermark_image
from .svg import watermark_svg_by_convert
from .options import WatermarkOptions
from .pdf import watermark_pdf
from .ppt import watermark_pptx
from .word import watermark_docx
from .common import safe_output_path


def watermark_file(input_path: Path, output_dir: Optional[Path], options: WatermarkOptions) -> Path:
    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在：{input_path}")

    file_type = detect_file_type(input_path)

    if file_type == "docx":
        out = safe_output_path(input_path, output_dir, options.suffix, ".docx")
        return watermark_docx(input_path, out, options)

    if file_type in SUPPORTED_WORD_LEGACY:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            if options.legacy_target == "editable":
                converted = convert_with_libreoffice(input_path, "docx", td_path)
                if converted:
                    out = safe_output_path(input_path, output_dir, options.suffix, ".docx")
                    return watermark_docx(converted, out, options)

            converted_pdf = convert_with_libreoffice(input_path, "pdf", td_path)
            if converted_pdf:
                out = safe_output_path(input_path, output_dir, options.suffix, ".pdf")
                return watermark_pdf(converted_pdf, out, options)

            raise RuntimeError(f"{input_path.name} 是旧版/非 OOXML 文档，需要 LibreOffice 转换后才能处理。")

    if file_type in SUPPORTED_EXCEL_OOXML:
        out = safe_output_path(input_path, output_dir, options.suffix, input_path.suffix or ".xlsx")
        return watermark_xlsx(input_path, out, options)

    if file_type in SUPPORTED_EXCEL_LEGACY:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            if options.legacy_target == "editable":
                converted = convert_with_libreoffice(input_path, "xlsx", td_path)
                if converted:
                    out = safe_output_path(input_path, output_dir, options.suffix, ".xlsx")
                    return watermark_xlsx(converted, out, options)

            converted_pdf = convert_with_libreoffice(input_path, "pdf", td_path)
            if converted_pdf:
                out = safe_output_path(input_path, output_dir, options.suffix, ".pdf")
                return watermark_pdf(converted_pdf, out, options)

            raise RuntimeError(f"{input_path.name} 是旧版或非 OOXML 表格文件，需要 LibreOffice 转换后才能处理。")

    if file_type == "pdf":
        out = safe_output_path(input_path, output_dir, options.suffix, ".pdf")
        return watermark_pdf(input_path, out, options)

    if file_type == "pptx":
        out = safe_output_path(input_path, output_dir, options.suffix, ".pptx")
        return watermark_pptx(input_path, out, options)

    if file_type in SUPPORTED_PPT_LEGACY:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            if options.legacy_target == "editable":
                converted = convert_with_libreoffice(input_path, "pptx", td_path)
                if converted:
                    out = safe_output_path(input_path, output_dir, options.suffix, ".pptx")
                    return watermark_pptx(converted, out, options)

            converted_pdf = convert_with_libreoffice(input_path, "pdf", td_path)
            if converted_pdf:
                out = safe_output_path(input_path, output_dir, options.suffix, ".pdf")
                return watermark_pdf(converted_pdf, out, options)

            raise RuntimeError(f"{input_path.name} 是旧版 PPT，需要 LibreOffice 转换后才能处理。")

    if file_type in SUPPORTED_IMAGES:
        ext = input_path.suffix if input_path.suffix else f".{file_type}"
        out = safe_output_path(input_path, output_dir, options.suffix, ext)
        return watermark_image(input_path, out, options)

    if file_type == "gif":
        out = safe_output_path(input_path, output_dir, options.suffix, ".gif")
        return watermark_gif(input_path, out, options)

    if file_type == "svg":
        out = safe_output_path(input_path, output_dir, options.suffix, ".png")
        return watermark_svg_by_convert(input_path, out, options)

    raise RuntimeError(f"暂不支持该文件格式：{file_type}，文件：{input_path.name}")
