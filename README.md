# universal-watermark

[中文文档](README_zh-CN.md)

![License](https://img.shields.io/github/license/czhanp/universal_watermark)
![Stars](https://img.shields.io/github/stars/czhanp/universal_watermark?style=social)
![npm](https://img.shields.io/npm/v/@czhanp/universal-watermark-skill)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

A code-first multi-format watermarking **Agent Skill** and **Python CLI** for Word, PDF, PowerPoint, Excel, images, and GIFs.

`universal-watermark` automatically detects file types, chooses the correct processor, applies visible text watermarks, and writes new output files without overwriting the original files.

## Why this project?

Most watermark tools focus on one format, usually PDF or images. This project is built for mixed real-world files:

- Word, PDF, PowerPoint, Excel, images, and GIFs;
- automatic file type detection;
- repeated, diagonal, semi-transparent text watermarks;
- batch processing from one command;
- safe output rules that keep the original file unchanged;
- reusable Agent Skill installation through npm.

## Preview

The following preview shows watermark effects on PDF, Word, image, Excel, and PowerPoint files.

<img src="example/show.png" alt="universal-watermark preview" width="100%">

## Quick Start

Install Python dependencies:

```bash
pip install pillow lxml python-docx pymupdf python-pptx
```

Add a watermark to one file:

```bash
python scripts/universal_watermark.py input.pdf --text "CONFIDENTIAL"
```

Batch process multiple files:

```bash
python scripts/universal_watermark.py a.docx b.pdf c.pptx table.xlsx image.jpg --output-dir watermarked --text "INTERNAL USE"
```

Use a Chinese font when needed:

```bash
python scripts/universal_watermark.py input.pdf --text "试用水印" --font-path "C:\Windows\Fonts\msyh.ttc"
```

## Install as an Agent Skill

This repository can be installed as a local Skill for Codex, Claude Code, or other agent workflows.

```bash
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

Default installation targets:

```text
~/.codex/skills/universal-watermark
~/.claude/skills/universal-watermark
~/.agents/skills/universal-watermark
```

Install for one target only:

```bash
universal-watermark-skill install --target codex
universal-watermark-skill install --target claude
universal-watermark-skill install --target agents
```

Run the installer once without keeping the npm package globally:

```bash
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

The npm package is used to distribute the Skill files. The actual watermarking logic is implemented in Python, so Python dependencies still need to be installed separately.

## Supported Formats

| Category | Formats |
|---|---|
| Word | `.docx`, `.doc`, `.rtf`, `.odt` |
| PDF | `.pdf` |
| PowerPoint | `.pptx`, `.ppt` |
| Excel | `.xlsx`, `.xlsm`, `.xltx`, `.xltm`, `.xls`, `.ods`, `.csv` |
| Images | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff` |
| Animated images | `.gif` |

Legacy Office and non-OOXML formats such as `.doc`, `.ppt`, `.xls`, `.rtf`, `.odt`, `.ods`, and `.csv` may require LibreOffice conversion before watermarking.

## Common CLI Examples

### Word / DOCX

```bash
python scripts/universal_watermark.py report.docx --text "Trial Watermark" --angle 45 --opacity 0.18
```

### PDF

```bash
python scripts/universal_watermark.py paper.pdf --text "Internal Use" --opacity 0.15
```

### PowerPoint

```bash
python scripts/universal_watermark.py slides.pptx --text "Draft" --angle -45
```

### Excel

Use worksheet background watermark:

```bash
python scripts/universal_watermark.py table.xlsx --text "Trial Watermark" --excel-mode background
```

Use transparent overlay watermark for printing or PDF export:

```bash
python scripts/universal_watermark.py table.xlsx --text "Trial Watermark" --excel-mode overlay --opacity 0.12
```

Use both modes:

```bash
python scripts/universal_watermark.py table.xlsx --text "Trial Watermark" --excel-mode both --opacity 0.10
```

### Images

```bash
python scripts/universal_watermark.py image.jpg --text "Trial Watermark"
```

### GIF

```bash
python scripts/universal_watermark.py animation.gif --text "Trial Watermark"
```

### Legacy Office Files

Convert to editable modern Office format before watermarking:

```bash
python scripts/universal_watermark.py old.doc --legacy-target editable
python scripts/universal_watermark.py old.ppt --legacy-target editable
python scripts/universal_watermark.py old.xls --legacy-target editable
```

Convert to PDF before watermarking:

```bash
python scripts/universal_watermark.py old.doc --legacy-target pdf
```

## Watermark Layouts

### `checkerboard`

`checkerboard` is the recommended visual layout. It alternates text slots and empty slots to avoid overly dense repeated watermarks.

```bash
python scripts/universal_watermark.py input.pdf \
  --text "Trial Watermark" \
  --layout checkerboard \
  --spacing-x-font-multiplier 2.0 \
  --spacing-y-font-multiplier 3.0 \
  --empty-slot-multiplier 1.0
```

### `staggered`

`staggered` is the traditional tiled watermark layout where every other row is shifted horizontally.

```bash
python scripts/universal_watermark.py input.pdf --text "Trial Watermark" --layout staggered
```

## Common Options

| Option | Description | Example |
|---|---|---|
| `--text` | Watermark text | `--text "Trial Watermark"` |
| `--angle` | Rotation angle | `--angle 45` |
| `--opacity` | Watermark opacity, from `0` to `1` | `--opacity 0.18` |
| `--color` | RGB color or hex color | `--color "#808080"` |
| `--font-path` | Path to a font file | `--font-path "C:\Windows\Fonts\msyh.ttc"` |
| `--layout` | Watermark layout | `--layout checkerboard` |
| `--output-dir` | Output directory | `--output-dir watermarked` |
| `--suffix` | Output filename suffix | `--suffix "_watermarked"` |
| `--legacy-target` | Legacy file conversion target | `--legacy-target editable` |
| `--excel-mode` | Excel watermark mode | `--excel-mode background` |

Check the current CLI help before using advanced options:

```bash
python scripts/universal_watermark.py --help
```

## Excel Watermark Modes

Excel does not provide a native watermark layer like Word. This project provides practical alternatives:

| Mode | Description | Best for |
|---|---|---|
| `background` | Adds a worksheet background image | Viewing and editing |
| `overlay` | Adds transparent image overlays | Printing and PDF export |
| `both` | Uses both background and overlay | Strongest visible effect |

Recommended default:

```bash
--excel-mode background
```

For printing or exporting to PDF:

```bash
--excel-mode overlay --opacity 0.12
```

## Output Rules

The tool never overwrites the original file by default.

```text
report.docx    -> report_watermarked.docx
paper.pdf      -> paper_watermarked.pdf
slides.pptx    -> slides_watermarked.pptx
table.xlsx     -> table_watermarked.xlsx
image.jpg      -> image_watermarked.jpg
```

If the output file already exists, a numeric suffix is added automatically:

```text
report_watermarked.docx
report_watermarked_1.docx
report_watermarked_2.docx
```

## Project Structure

```text
universal-watermark/
  SKILL.md
  README.md
  README_zh-CN.md
  LICENSE
  package.json
  bin/
    install.js
  scripts/
    universal_watermark.py
    watermark/
      cli.py
      detector.py
      dispatcher.py
      word.py
      pdf.py
      ppt.py
      excel.py
      image.py
      gif.py
      converters.py
      common.py
      options.py
      constants.py
      svg.py
  example/
```

## Notes and Limitations

- Legacy Office files such as `.doc`, `.ppt`, and `.xls` require conversion before watermarking.
- LibreOffice conversion may cause slight layout differences.
- PDF watermarking overlays watermark content onto pages, so low opacity is recommended.
- Excel `background` mode usually does not appear in printing.
- Excel `overlay` mode is more suitable for printing but may affect cell selection.
- GIF output may have slight quality changes because of palette limitations.
- Very large images or multi-page TIFF files may require more memory.
- Encrypted PDFs require appropriate permission before processing.

## Development

Check Python syntax:

```bash
python -m compileall scripts
```

Show CLI help:

```bash
python scripts/universal_watermark.py --help
```

Suggested maintenance areas:

| Module | Purpose |
|---|---|
| `scripts/watermark/word.py` | Word / DOCX watermarking |
| `scripts/watermark/pdf.py` | PDF watermarking |
| `scripts/watermark/ppt.py` | PowerPoint / PPTX watermarking |
| `scripts/watermark/excel.py` | Excel / XLSX / XLSM watermarking |
| `scripts/watermark/image.py` | Static image watermarking |
| `scripts/watermark/gif.py` | Animated GIF watermarking |
| `scripts/watermark/common.py` | Shared watermark layer, font, and OOXML utilities |
| `scripts/watermark/options.py` | Watermark option definitions |

## License

MIT License.
