---
name: universal-watermark
description: >
  Add visible text watermarks to Word, PDF, PowerPoint, Excel, image, and GIF files.
  Use this skill when the user asks to add, apply, insert, customize, batch process,
  or automatically apply watermarks to .doc, .docx, .pdf, .ppt, .pptx, .xls, .xlsx,
  .xlsm, .ods, .csv, .png, .jpg, .jpeg, .webp, .bmp, .tif, .tiff, or .gif files.
  当用户要求给文档、PDF、PPT、Excel、图片或 GIF 添加水印、斜向水印、平铺水印、
  半透明水印、批量水印，或要求自动识别文件格式并添加水印时，使用本技能。
  Prefer running scripts/universal_watermark.py first, preserve original files,
  and create watermarked output copies.
---

# Universal Watermark Skill

## 1. Skill Purpose

This skill adds visible text watermarks to multiple file formats, including:

- Word documents: `.doc`, `.docx`
- PDF documents: `.pdf`
- PowerPoint files: `.ppt`, `.pptx`
- Excel and spreadsheet files: `.xls`, `.xlsx`, `.xlsm`, `.ods`, `.csv`
- Images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff`
- GIF files: `.gif`

The skill is designed for watermarking workflows such as:

- adding a diagonal watermark;
- adding repeated or tiled watermarks;
- adding semi-transparent visible watermarks;
- batch processing multiple files;
- automatically choosing the correct processing method based on file extension;
- preserving the original file and generating a new watermarked output file.

## 2. Core Rule: Prefer the Existing Code

This skill is code-first.

When the user provides files and asks for watermarking, do not start by writing a new watermark implementation from scratch. First use the existing Python entry script:

```bash
python scripts/universal_watermark.py --help
```

Then run the script with the user’s input file and watermark text.

Preferred basic pattern:

```bash
python scripts/universal_watermark.py <input_file> --text "<watermark_text>"
```

Example:

```bash
python scripts/universal_watermark.py input.docx --text "CONFIDENTIAL"
```

Example with angle:

```bash
python scripts/universal_watermark.py input.pdf --text "CONFIDENTIAL" --angle 45
```

Example with an output path:

```bash
python scripts/universal_watermark.py input.xlsx --text "CONFIDENTIAL" --output output_watermarked.xlsx
```

If the exact parameters are uncertain, always inspect the current CLI help first:

```bash
python scripts/universal_watermark.py --help
```

The CLI help and existing source code are the source of truth.

## 3. When to Modify Code

Only inspect or modify the implementation code when one of the following is true:

- the existing script fails;
- the user asks to add a new file format;
- the user asks for a new watermark style or parameter;
- a supported format produces incorrect output;
- the user explicitly asks to improve the code;
- the current CLI does not expose a required option;
- layout preservation or output quality needs debugging.

When modifying code, keep the public CLI stable whenever possible.

## 4. Standard Workflow

Follow this order during normal use.

### Step 1: Identify the input file type

Check the file extension first.

Examples:

```text
.docx  -> Word workflow
.pdf   -> PDF workflow
.pptx  -> PowerPoint workflow
.xlsx  -> Excel workflow
.png   -> image workflow
.gif   -> GIF workflow
```

If several files are provided, group them by format and process each file with the proper workflow.

### Step 2: Read the user’s watermark requirements

Extract these details from the user request:

- watermark text;
- target files or folder;
- output location;
- angle;
- opacity;
- font size;
- color;
- spacing;
- position;
- whether the watermark should be repeated or centered;
- whether batch processing is required.

If the user does not specify details, choose safe defaults:

```text
angle: 45 degrees
opacity: semi-transparent
position: repeated diagonal watermark
output: new file beside the original
overwrite: false
```

### Step 3: Run the existing CLI

Use:

```bash
python scripts/universal_watermark.py <input_file> --text "<watermark_text>"
```

For batch workflows, prefer the script’s built-in batch or folder option if available. Confirm available parameters with:

```bash
python scripts/universal_watermark.py --help
```

### Step 4: Verify the output

After processing, check that:

- the output file exists;
- the original file was not overwritten unless explicitly requested;
- the watermark is visible;
- the file extension matches the expected output format;
- the output can be opened or inspected.

### Step 5: Report results clearly

Tell the user:

- which files were processed;
- where the output files were saved;
- which files failed, if any;
- what fallback or limitation was used, if applicable.

## 5. File Preservation Rules

Always preserve the original file by default.

Do not overwrite the original input file unless the user explicitly asks for overwrite behavior.

Preferred output naming:

```text
input.docx      -> input_watermarked.docx
input.pdf       -> input_watermarked.pdf
input.xlsx      -> input_watermarked.xlsx
image.png       -> image_watermarked.png
animation.gif   -> animation_watermarked.gif
```

If an output path is provided by the user, use the provided path.

If an output file already exists, avoid overwriting it unless the user explicitly allows overwriting. Use a numbered suffix when needed:

```text
input_watermarked_1.pdf
input_watermarked_2.pdf
```

## 6. Supported Format Strategy

### Word: `.doc`, `.docx`

For Word documents:

- preserve the editable document structure as much as possible;
- prefer adding a real document watermark when supported;
- avoid flattening the document into images unless no safe alternative exists;
- for legacy `.doc`, use conversion if the implementation requires `.docx`.

### PDF: `.pdf`

For PDFs:

- create a new watermarked copy;
- preserve existing pages;
- apply watermark on each page;
- avoid changing page size, page order, or existing text content.

### PowerPoint: `.ppt`, `.pptx`

For PowerPoint files:

- preserve slide order and layout;
- apply watermark to each slide;
- keep original objects when possible;
- for legacy `.ppt`, use conversion if the implementation requires `.pptx`.

### Excel: `.xls`, `.xlsx`, `.xlsm`, `.ods`, `.csv`

For spreadsheets:

- preserve workbook content and sheet structure;
- apply visible watermark in a way suitable for spreadsheet output;
- avoid damaging formulas, values, merged cells, charts, and formatting;
- for `.csv`, treat it as a spreadsheet-like input, but remember that CSV cannot preserve rich formatting.

### Images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff`

For images:

- keep the image dimensions unless the user requests resizing;
- preserve transparency when possible;
- apply watermark with readable opacity and spacing;
- save to a reasonable output format matching the input extension.

### GIF: `.gif`

For GIF files:

- preserve animation when possible;
- apply watermark to all frames;
- keep frame duration and loop behavior when possible;
- if animation cannot be preserved, clearly explain the limitation.

## 7. Common Commands

### View help

```bash
python scripts/universal_watermark.py --help
```

Meaning:

```text
Shows the current command-line options supported by the watermark script.
Use this before relying on parameters that may have changed.
```

### Add a basic watermark

```bash
python scripts/universal_watermark.py input.pdf --text "CONFIDENTIAL"
```

Meaning:

```text
Adds the text watermark CONFIDENTIAL to input.pdf and creates a watermarked output file.
```

### Add a diagonal watermark

```bash
python scripts/universal_watermark.py input.docx --text "CONFIDENTIAL" --angle 45
```

Meaning:

```text
Adds a 45-degree diagonal watermark to the Word document.
```

### Specify output file

```bash
python scripts/universal_watermark.py input.xlsx --text "CONFIDENTIAL" --output output_watermarked.xlsx
```

Meaning:

```text
Writes the watermarked result to the specified output path.
```

### Process an image

```bash
python scripts/universal_watermark.py image.png --text "CONFIDENTIAL"
```

Meaning:

```text
Adds a visible watermark to the image and saves a new watermarked image.
```

### Process a GIF

```bash
python scripts/universal_watermark.py animation.gif --text "CONFIDENTIAL"
```

Meaning:

```text
Adds a visible watermark to the GIF frames while preserving animation when supported.
```

### Batch processing

If the script supports folder or batch parameters, prefer them.

Check first:

```bash
python scripts/universal_watermark.py --help
```

Then use the available batch option.

Typical pattern:

```bash
python scripts/universal_watermark.py <input_folder> --text "CONFIDENTIAL" --batch
```

If no built-in batch option exists, process files one by one with the same CLI entry script.

## 8. Dependency Handling

Before running the tool, check that Python is available:

```bash
python --version
```

If `python` is not available on macOS or Linux, try:

```bash
python3 --version
```

When dependencies are missing, inspect project files first:

```text
requirements.txt
pyproject.toml
package.json
README.md
README_zh-CN.md
```

Install Python dependencies according to the repository instructions.

Common pattern:

```bash
pip install -r requirements.txt
```

Do not invent dependency lists when the repository already provides installation instructions.

## 9. Repository Structure Reference

The repository may contain files similar to:

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
      word.py
      pdf.py
      ppt.py
      excel.py
      image.py
      gif.py
  example/
  examples/
```

Use this section only as a maintenance reference.

During normal watermarking tasks, start from:

```bash
python scripts/universal_watermark.py --help
```

Do not read every module unless debugging or extending the implementation.

## 10. npm / npx Usage

If the skill is installed from npm, the package may expose a command such as:

```bash
universal-watermark-skill --help
```

or:

```bash
universal-watermark --help
```

For one-time npm execution, use the command documented in the current README.

Do not assume npx behavior without checking `package.json`:

```json
"bin": {
  "universal-watermark-skill": "bin/install.js"
}
```

The `bin` field determines which executable command npm or npx can run.

## 11. Troubleshooting

### Problem: The script cannot find the input file

Check:

```bash
pwd
ls
```

or on Windows PowerShell:

```powershell
Get-Location
Get-ChildItem
```

Use quoted paths when paths contain spaces:

```bash
python scripts/universal_watermark.py "C:\Users\Name\Desktop\input file.pdf" --text "CONFIDENTIAL"
```

### Problem: A format is unsupported

Do not pretend it succeeded.

Explain the unsupported format and suggest one of these options:

- convert the file to a supported format;
- process the closest supported representation;
- extend the code to support the format.

### Problem: Word, PowerPoint, or Excel legacy formats fail

For old Office formats such as `.doc`, `.ppt`, or `.xls`, conversion may be required.

Explain that legacy binary Office formats are harder to edit directly than modern XML-based formats such as:

```text
.docx
.pptx
.xlsx
```

### Problem: PDF output looks different

PDF watermarking should preserve page size and content. If output appearance changes, check whether the script rasterized pages or changed page boxes.

Prefer vector/text overlay workflows when available.

### Problem: GIF becomes static

GIF watermarking must preserve frames. If the output becomes static, the implementation likely processed only the first frame.

Fix by applying the watermark frame by frame and saving the full animation.

### Problem: Chinese characters do not display correctly

Use a font that supports Chinese characters.

On Windows, common font choices include:

```text
Microsoft YaHei
SimSun
```

If the script accepts a font path, provide an explicit font file path.

## 12. Safety and Quality Rules

Always follow these rules:

- preserve original files by default;
- create output copies;
- avoid destructive overwrites;
- do not remove existing content;
- do not silently change file format;
- do not claim success without checking output;
- report failed files separately;
- use the existing CLI before writing new code;
- use current `--help` output as the source of truth for available options.

## 13. Response Style

When reporting to the user, be direct and practical.

Good response pattern:

```text
已完成水印处理。

输入文件：
- input.pdf

输出文件：
- input_watermarked.pdf

水印参数：
- text: CONFIDENTIAL
- angle: 45
- mode: repeated diagonal watermark

备注：
- 原文件未被覆盖。
```

If something failed:

```text
以下文件处理失败：

- old_file.doc

原因：
- 当前脚本无法直接处理该 legacy Office 格式。

建议：
- 先转换为 .docx 后重新处理；
- 或扩展脚本中的 Word legacy format handling。
```

## 14. Important Reminder

This skill should behave like a reliable file-processing tool, not like a loose explanation template.

For actual watermarking tasks:

```text
inspect CLI help -> run existing script -> verify output -> report result
```

For development tasks:

```text
inspect code -> modify minimal necessary module -> test with sample files -> update documentation if behavior changes
```