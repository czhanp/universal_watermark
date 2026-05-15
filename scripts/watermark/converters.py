from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def find_soffice() -> Optional[str]:
    for name in ["soffice", "libreoffice"]:
        p = shutil.which(name)
        if p:
            return p
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def convert_with_libreoffice(input_path: Path, target_ext: str, output_dir: Path) -> Optional[Path]:
    soffice = find_soffice()
    if not soffice:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [soffice, "--headless", "--convert-to", target_ext, "--outdir", str(output_dir), str(input_path)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    expected = output_dir / f"{input_path.stem}.{target_ext}"

    if proc.returncode == 0 and expected.exists() and expected.stat().st_size > 0:
        return expected

    for m in output_dir.glob(f"{input_path.stem}.*"):
        if m.suffix.lower().lstrip(".") == target_ext.lower() and m.stat().st_size > 0:
            return m

    return None
