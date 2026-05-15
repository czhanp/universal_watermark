from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .common import normalize_opacity
from .detector import detect_file_type
from .dispatcher import watermark_file
from .options import WatermarkOptions


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.strip()
    if value.startswith("#"):
        value = value[1:]
        if len(value) != 6:
            raise argparse.ArgumentTypeError("颜色十六进制格式应为 #RRGGBB")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))  # type: ignore
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("颜色格式应为 #RRGGBB 或 R,G,B")
    nums = tuple(int(p) for p in parts)
    if any(n < 0 or n > 255 for n in nums):
        raise argparse.ArgumentTypeError("RGB 数值应在 0-255")
    return nums  # type: ignore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="多格式文件水印工具：自动识别 DOCX/PDF/PPTX/XLSX/图片/GIF，并添加倾斜平铺水印。")
    parser.add_argument("inputs", nargs="+", help="输入文件路径，可一次传入多个文件。")
    parser.add_argument("-o", "--output-dir", default=None, help="输出目录。不填则输出到原文件所在目录。")
    parser.add_argument("--text", default="内部资料", help="水印文字，默认：内部资料")
    parser.add_argument("--angle", type=float, default=45.0, help="倾斜角度，默认 45")
    parser.add_argument("--opacity", type=float, default=0.18, help="透明度。支持 0-1 或 0-255，例如 0.18 或 45。")
    parser.add_argument("--color", type=parse_color, default=(120, 120, 120), help="颜色，#RRGGBB 或 R,G,B")
    parser.add_argument("--font-path", default=None, help="字体路径，中文建议指定微软雅黑/黑体/Noto CJK")
    parser.add_argument("--font-size-ratio", type=float, default=0.055, help="字号比例，相对于页面/图片宽度")
    parser.add_argument("--layout", choices=["checkerboard", "staggered"], default="checkerboard", help="水印排布：checkerboard=文字槽/空槽交叉排布；staggered=旧版错行平铺")
    parser.add_argument("--spacing-x-ratio", type=float, default=0.32, help="旧版 staggered 模式的横向间距比例")
    parser.add_argument("--spacing-y-ratio", type=float, default=0.18, help="旧版 staggered 模式的纵向间距比例")
    parser.add_argument("--spacing-x-font-multiplier", type=float, default=0.5, help="checkerboard 模式横向间距：字体行高的倍数，默认 0.5")
    parser.add_argument("--spacing-y-font-multiplier", type=float, default=1.5, help="纵向行距相对于字体行高的倍数；checkerboard 默认 1.5")
    parser.add_argument("--empty-slot-multiplier", type=float, default=1.0, help="checkerboard 模式空槽宽度倍数：空槽宽度=文字槽宽度×该值，默认 1.0")
    parser.add_argument("--suffix", default="_加水印", help="输出文件名后缀，默认：_加水印")
    parser.add_argument("--dpi", type=int, default=150, help="生成水印图的 DPI，默认 150")
    parser.add_argument("--jpeg-quality", type=int, default=95, help="JPEG/WEBP 输出质量，默认 95")
    parser.add_argument("--legacy-target", choices=["editable", "pdf"], default="editable", help="旧版 doc/ppt/xls 的目标：editable=优先转 docx/pptx/xlsx；pdf=优先转 pdf")
    parser.add_argument("--excel-mode", choices=["background", "overlay", "both"], default="background", help="Excel 水印模式：background=工作表背景，不遮挡编辑但通常不打印；overlay=透明浮层，可能打印但会覆盖单元格；both=两者都加")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    options = WatermarkOptions(
        text=args.text,
        angle=args.angle,
        opacity=normalize_opacity(args.opacity),
        color=args.color,
        font_size_ratio=args.font_size_ratio,
        layout=args.layout,
        spacing_x_ratio=args.spacing_x_ratio,
        spacing_y_ratio=args.spacing_y_ratio,
        spacing_y_font_multiplier=args.spacing_y_font_multiplier,
        spacing_x_font_multiplier=args.spacing_x_font_multiplier,
        empty_slot_multiplier=args.empty_slot_multiplier,
        font_path=args.font_path,
        suffix=args.suffix,
        legacy_target=args.legacy_target,
        excel_mode=args.excel_mode,
        dpi=args.dpi,
        jpeg_quality=args.jpeg_quality,
    )

    output_dir = Path(args.output_dir).resolve() if args.output_dir else None

    ok = 0
    failed = 0
    for item in args.inputs:
        path = Path(item)
        try:
            file_type = detect_file_type(path)
            out = watermark_file(path, output_dir, options)
            print(f"[OK] {path.name} | 类型: {file_type} | 输出: {out}")
            ok += 1
        except Exception as e:
            print(f"[ERROR] {path} | {e}", file=sys.stderr)
            failed += 1

    print(f"完成：成功 {ok} 个，失败 {failed} 个。")
    return 0 if failed == 0 else 1
