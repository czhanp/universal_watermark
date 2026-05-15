from __future__ import annotations

import zipfile
from pathlib import Path

from .constants import SUPPORTED_EXCEL_OOXML, SUPPORTED_IMAGES


def detect_file_type(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    with path.open("rb") as f:
        head = f.read(16)

    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "gif"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if head.startswith(b"BM"):
        return "bmp"
    if head[:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    if head[:4] == b"RIFF":
        return "webp" if ext == "webp" else ext

    if zipfile.is_zipfile(path):
        try:
            with zipfile.ZipFile(path, "r") as z:
                names = set(z.namelist())
            if "word/document.xml" in names:
                return "docx"
            if "ppt/presentation.xml" in names:
                return "pptx"
            if "xl/workbook.xml" in names:
                return ext if ext in SUPPORTED_EXCEL_OOXML else "xlsx"
        except Exception:
            pass

    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        if ext in {"doc", "ppt", "xls"}:
            return ext
        return "ole"

    if ext in {"docx", "doc", "rtf", "odt", "pdf", "pptx", "ppt", "gif", "xlsx", "xlsm", "xltx", "xltm", "xls", "ods", "csv"}:
        return ext
    if ext in SUPPORTED_IMAGES:
        return "jpg" if ext == "jpeg" else ext
    if ext == "svg":
        return "svg"
    return ext or "unknown"
