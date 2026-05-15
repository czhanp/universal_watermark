from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .constants import CT_NS, EMU_PER_INCH, PKG_REL_NS, PT_PER_INCH
from .options import WatermarkOptions


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def normalize_opacity(value: float) -> float:
    if value > 1:
        value = value / 255.0
    return max(0.0, min(1.0, value))


def safe_output_path(input_path: Path, output_dir: Optional[Path], suffix: str, ext: Optional[str] = None) -> Path:
    out_dir = output_dir or input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = ext or input_path.suffix
    if not ext.startswith("."):
        ext = "." + ext
    candidate = out_dir / f"{input_path.stem}{suffix}{ext}"
    if not candidate.exists():
        return candidate
    i = 1
    while True:
        candidate = out_dir / f"{input_path.stem}{suffix}_{i}{ext}"
        if not candidate.exists():
            return candidate
        i += 1


def find_font(font_path: Optional[str] = None) -> str:
    candidates = [
        font_path,
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if p and Path(p).exists():
            return str(p)
    raise FileNotFoundError("未找到可用字体。请通过 --font-path 指定中文字体，例如 C:/Windows/Fonts/msyh.ttc")


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return max(1, bbox[2] - bbox[0]), max(1, bbox[3] - bbox[1])


def font_line_height(font: ImageFont.FreeTypeFont) -> int:
    """返回字体自身行高，优先使用字体度量值。"""
    try:
        ascent, descent = font.getmetrics()
        line_height = int(ascent + descent)
        if line_height > 0:
            return line_height
    except Exception:
        pass

    bbox = font.getbbox("Ag中文水印")
    return max(1, int(bbox[3] - bbox[1]))


def paste_checkerboard_watermarks(
    layer: Image.Image,
    rotated: Image.Image,
    *,
    width_px: int,
    height_px: int,
    line_height: int,
    options: WatermarkOptions,
) -> None:
    """
    文字槽 / 空槽交叉排布。

    第 1 行：文字  + 横向间距 + 空槽 + 横向间距 + 文字...
    第 2 行：空槽  + 横向间距 + 文字 + 横向间距 + 空槽...
    第 3 行：回到第 1 行。

    纵向行距按字体自身行高乘以 spacing_y_font_multiplier 计算，
    而不是按页面高度比例计算。
    """
    rw, rh = rotated.size

    text_slot_w = rw
    empty_slot_w = max(rw, int(rw * max(0.1, options.empty_slot_multiplier)))

    gap_x = max(1, int(line_height * options.spacing_x_font_multiplier))

    # 未显式设置时，给 checkerboard 一个相对紧密的默认值。
    # 如果用户希望更密或更疏，直接传 --spacing-y-font-multiplier 调整。
    row_multiplier = options.spacing_y_font_multiplier
    if row_multiplier is None:
        row_multiplier = 1.5
    row_step = max(1, int(line_height * row_multiplier))

    cycle_w = text_slot_w + gap_x + empty_slot_w + gap_x

    start_x = -cycle_w
    end_x = width_px + cycle_w
    start_y = -rh
    end_y = height_px + rh

    row = 0
    y = start_y
    while y < end_y:
        x = start_x
        while x < end_x:
            if row % 2 == 0:
                # 文字放在“文字槽”中。
                paste_x = x
            else:
                # 文字放在上一行的“空槽”中，并在空槽内居中。
                paste_x = x + text_slot_w + gap_x + (empty_slot_w - rw) / 2

            layer.alpha_composite(rotated, (int(paste_x), int(y)))
            x += cycle_w

        y += row_step
        row += 1


def paste_staggered_watermarks(
    layer: Image.Image,
    rotated: Image.Image,
    *,
    width_px: int,
    height_px: int,
    font_size: int,
    options: WatermarkOptions,
) -> None:
    """旧版错行平铺：每一行都有文字，相邻行横向错开半个 spacing。"""
    rw, rh = rotated.size
    spacing_x = max(rw + 20, int(width_px * options.spacing_x_ratio))
    if options.spacing_y_font_multiplier is not None:
        spacing_y = max(1, int(font_size * options.spacing_y_font_multiplier))
    else:
        spacing_y = max(rh + 20, int(height_px * options.spacing_y_ratio))

    start_x = -rw
    start_y = -rh
    end_x = width_px + rw
    end_y = height_px + rh

    row = 0
    y = start_y
    while y < end_y:
        x_offset = 0 if row % 2 == 0 else spacing_x // 2
        x = start_x - x_offset
        while x < end_x:
            layer.alpha_composite(rotated, (int(x), int(y)))
            x += spacing_x
        y += spacing_y
        row += 1


def create_watermark_layer(width_px: int, height_px: int, options: WatermarkOptions, font_path: Optional[str] = None) -> Image.Image:
    width_px = int(max(1, width_px))
    height_px = int(max(1, height_px))

    font_path = font_path or find_font(options.font_path)
    font_size = max(12, int(width_px * options.font_size_ratio))
    font = ImageFont.truetype(font_path, font_size)
    line_height = font_line_height(font)

    alpha = int(round(normalize_opacity(options.opacity) * 255))
    color = (*options.color, alpha)

    layer = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 0))
    dummy = ImageDraw.Draw(layer)
    tw, th = text_bbox(dummy, options.text, font)

    # 用较小 padding 生成更紧凑的文字图块，避免“文字槽/空槽”被过多透明边距撑大。
    pad = max(6, int(font_size * 0.18))
    tile_h = max(th, line_height)
    tile = Image.new("RGBA", (tw + pad * 2, tile_h + pad * 2), (255, 255, 255, 0))
    td = ImageDraw.Draw(tile)
    td.text((pad, pad + (tile_h - th) / 2), options.text, font=font, fill=color)

    resampling = getattr(Image, "Resampling", Image).BICUBIC
    rotated = tile.rotate(options.angle, expand=True, resample=resampling)

    layout = getattr(options, "layout", "checkerboard")
    if layout == "staggered":
        paste_staggered_watermarks(
            layer,
            rotated,
            width_px=width_px,
            height_px=height_px,
            font_size=font_size,
            options=options,
        )
    else:
        paste_checkerboard_watermarks(
            layer,
            rotated,
            width_px=width_px,
            height_px=height_px,
            line_height=line_height,
            options=options,
        )

    return layer

def layer_to_png_bytes(layer: Image.Image, dpi: int = 150) -> bytes:
    buf = io.BytesIO()
    layer.save(buf, format="PNG", dpi=(dpi, dpi))
    return buf.getvalue()


def emu_to_inches(emu: int) -> float:
    return emu / EMU_PER_INCH


def emu_to_pt(emu: int) -> float:
    return emu_to_inches(emu) * PT_PER_INCH


def read_xml_from_zip(z: zipfile.ZipFile, name: str):
    from lxml import etree
    return etree.fromstring(z.read(name))


def empty_relationships_root():
    from lxml import etree
    return etree.Element(qn(PKG_REL_NS, "Relationships"), nsmap={None: PKG_REL_NS})


def next_rid(rels_root) -> str:
    max_id = 0
    for rel in rels_root.findall(qn(PKG_REL_NS, "Relationship")):
        rid = rel.get("Id", "")
        m = re.fullmatch(r"rId(\d+)", rid)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return f"rId{max_id + 1}"


def add_png_content_type(content_types_root) -> None:
    from lxml import etree
    for node in content_types_root.findall(qn(CT_NS, "Default")):
        if node.get("Extension") == "png":
            return
    etree.SubElement(
        content_types_root,
        qn(CT_NS, "Default"),
        {"Extension": "png", "ContentType": "image/png"},
    )


def add_override_content_type(content_types_root, part_name: str, content_type: str) -> None:
    """向 [Content_Types].xml 添加 Override，已存在则不重复添加。"""
    from lxml import etree
    part_name = "/" + part_name.lstrip("/")
    for node in content_types_root.findall(qn(CT_NS, "Override")):
        if node.get("PartName") == part_name:
            return
    etree.SubElement(
        content_types_root,
        qn(CT_NS, "Override"),
        {"PartName": part_name, "ContentType": content_type},
    )


def rels_path_for_part(part_path: str) -> str:
    """根据包内 part 路径得到对应 .rels 路径。"""
    parent = "/".join(part_path.split("/")[:-1])
    name = part_path.split("/")[-1]
    return f"{parent}/_rels/{name}.rels"


def resolve_rel_target(source_part: str, target: str) -> str:
    """解析 OOXML 关系 Target 到包内规范路径。"""
    import posixpath
    if target.startswith("/"):
        return target.lstrip("/")
    base = posixpath.dirname(source_part)
    return posixpath.normpath(posixpath.join(base, target))

