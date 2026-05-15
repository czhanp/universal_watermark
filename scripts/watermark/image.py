from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, ImageSequence

from .common import create_watermark_layer, find_font
from .options import WatermarkOptions


def watermark_image(input_path: Path, output_path: Path, options: WatermarkOptions) -> Path:
    ext = output_path.suffix.lower().lstrip(".")
    font = find_font(options.font_path)

    with Image.open(input_path) as im:
        if ext in {"tif", "tiff"} and getattr(im, "n_frames", 1) > 1:
            frames = []
            for frame in ImageSequence.Iterator(im):
                fr = ImageOps.exif_transpose(frame).convert("RGBA")
                layer = create_watermark_layer(fr.width, fr.height, options, font)
                fr.alpha_composite(layer)
                frames.append(fr.convert("RGB"))
            frames[0].save(output_path, save_all=True, append_images=frames[1:], compression="tiff_deflate")
            return output_path

        im = ImageOps.exif_transpose(im).convert("RGBA")
        layer = create_watermark_layer(im.width, im.height, options, font)
        im.alpha_composite(layer)

        if ext in {"jpg", "jpeg"}:
            im.convert("RGB").save(output_path, quality=options.jpeg_quality, optimize=True)
        elif ext == "bmp":
            im.convert("RGB").save(output_path)
        elif ext == "webp":
            im.save(output_path, quality=options.jpeg_quality, method=6)
        elif ext in {"tif", "tiff"}:
            im.convert("RGB").save(output_path, compression="tiff_deflate")
        else:
            im.save(output_path)
    return output_path
