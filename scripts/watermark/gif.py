from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageSequence

from .common import create_watermark_layer, find_font
from .options import WatermarkOptions


def watermark_gif(input_path: Path, output_path: Path, options: WatermarkOptions) -> Path:
    font = find_font(options.font_path)
    with Image.open(input_path) as im:
        loop = im.info.get("loop", 0)
        durations = []
        frames = []

        for frame in ImageSequence.Iterator(im):
            duration = frame.info.get("duration", im.info.get("duration", 100))
            durations.append(duration)
            fr = frame.convert("RGBA")
            layer = create_watermark_layer(fr.width, fr.height, options, font)
            fr.alpha_composite(layer)
            frames.append(fr.convert("P", palette=Image.Palette.ADAPTIVE))

        if not frames:
            raise RuntimeError("GIF 没有可处理的帧。")

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=loop,
            disposal=2,
            optimize=False,
        )
    return output_path
