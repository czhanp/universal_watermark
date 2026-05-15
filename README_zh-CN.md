# universal-watermark

[English](README.md)

一个支持 Word、PDF、PowerPoint、Excel、图片和 GIF 的多格式水印生成 **Skill / CLI 工具**。

`universal-watermark` 可以自动识别文件格式，并为文件添加可配置的倾斜、平铺、半透明文字水印。工具会根据不同格式选择对应的处理方式，优先保持原格式输出，并且不会覆盖原文件。

---

## 1. Skill 使用说明

本项目首先可以作为一个可复用的水印处理 Skill 包使用。

典型 Skill 包结构如下：

```text
universal-watermark/
  SKILL.md
  README.md
  README_zh-CN.md
  scripts/
    universal_watermark.py
    watermark/
      ...
```

### Skill 主要作用

当用户要求给文件添加水印时，Skill 应执行以下流程：

```text
识别文件类型
-> 选择对应格式的处理器
-> 生成透明平铺水印图层
-> 输出带水印的新文件
-> 不覆盖原始文件
```

### 适用请求

该 Skill 适用于以下场景：

```text
给这个 Word 文档加水印
给这个 PDF 添加平铺水印
给这个 PPT 添加草稿水印
给这个 Excel 表格添加水印
给这张图片添加水印
批量给这些文件加水印
自动识别文件格式并添加水印
```

### 典型触发关键词

```text
水印
添加水印
加水印
平铺水印
半透明水印
Word 水印
PDF 水印
PPT 水印
Excel 水印
图片水印
GIF 水印
批量水印
```

### Skill 处理原则

- 自动识别真实文件格式；
- 按不同文件格式选择不同处理逻辑；
- 能保持原格式时优先保持原格式；
- 不覆盖原始文件；
- 仅在必要时转换旧格式文件；
- 对 `.doc`、`.ppt`、`.xls`、`.rtf`、`.odt`、`.ods`、`.csv` 等格式说明转换风险。

### Skill 分格式处理路线

| 文件类型 | 处理路线 |
|---|---|
| `.docx` | 修改 DOCX 的 OOXML 页眉结构并插入整页透明水印图 |
| `.doc`、`.rtf`、`.odt` | 转换为 `.docx` 或 `.pdf` 后处理 |
| `.pdf` | 在每页叠加透明水印图 |
| `.pptx` | 在每张幻灯片中插入水印图 |
| `.ppt` | 转换为 `.pptx` 或 `.pdf` 后处理 |
| `.xlsx`、`.xlsm` | 修改 Excel OOXML，添加背景或浮层水印 |
| `.xls`、`.ods`、`.csv` | 转换为 `.xlsx` 或 `.pdf` 后处理 |
| 图片 | 使用 Pillow 合成水印图层 |
| `.gif` | 逐帧添加水印并重新保存 |

---

## 2. CLI 使用方法

除了作为 Skill 使用，本项目也可以直接作为 Python 命令行工具运行。

### 安装依赖

安装 Python 依赖：

```bash
pip install pillow lxml python-docx pymupdf python-pptx
```

可选依赖：

```bash
pip install cairosvg python-magic pillow-heif
```

如果需要处理 `.doc`、`.ppt`、`.xls`、`.rtf`、`.odt`、`.ods`、`.csv` 等旧格式或非 OOXML 格式，请安装 LibreOffice，并确保 `soffice` 或 `libreoffice` 命令可在系统 PATH 中使用。

Windows 常见安装路径：

```text
C:\Program Files\LibreOffice\program\soffice.exe
```

### 快速开始

给单个文件添加水印：

```bash
python scripts/universal_watermark.py input.pdf --text "试用水印"
```

批量处理多个文件：

```bash
python scripts/universal_watermark.py a.docx b.pdf c.pptx table.xlsx image.jpg --output-dir watermarked --text "内部资料"
```

中文水印建议显式指定中文字体，避免出现方块或缺字：

```bash
python scripts/universal_watermark.py input.pdf --text "试用水印" --font-path "C:\Windows\Fonts\msyh.ttc"
```

### 常用命令示例

#### Word / DOCX

```bash
python scripts/universal_watermark.py report.docx --text "试用水印" --angle 45 --opacity 0.18
```

#### PDF

```bash
python scripts/universal_watermark.py paper.pdf --text "内部资料" --opacity 0.15
```

#### PowerPoint

```bash
python scripts/universal_watermark.py slides.pptx --text "草稿" --angle -45
```

#### Excel

使用工作表背景水印：

```bash
python scripts/universal_watermark.py table.xlsx --text "试用水印" --excel-mode background
```

使用透明浮层水印，适合打印或导出 PDF：

```bash
python scripts/universal_watermark.py table.xlsx --text "试用水印" --excel-mode overlay --opacity 0.12
```

同时使用背景水印和浮层水印：

```bash
python scripts/universal_watermark.py table.xlsx --text "试用水印" --excel-mode both --opacity 0.10
```

#### 图片

```bash
python scripts/universal_watermark.py image.jpg --text "试用水印"
```

#### GIF 动图

```bash
python scripts/universal_watermark.py animation.gif --text "试用水印"
```

#### 旧版 Office 文件

优先转换为可编辑的新格式后加水印：

```bash
python scripts/universal_watermark.py old.doc --legacy-target editable
python scripts/universal_watermark.py old.ppt --legacy-target editable
python scripts/universal_watermark.py old.xls --legacy-target editable
```

如果只需要发布版，可以转换为 PDF 后加水印：

```bash
python scripts/universal_watermark.py old.doc --legacy-target pdf
```

---

## 3. 支持格式

| 类型 | 支持格式 |
|---|---|
| Word | `.docx`、`.doc`、`.rtf`、`.odt` |
| PDF | `.pdf` |
| PowerPoint | `.pptx`、`.ppt` |
| Excel | `.xlsx`、`.xlsm`、`.xltx`、`.xltm`、`.xls`、`.ods`、`.csv` |
| 图片 | `.png`、`.jpg`、`.jpeg`、`.webp`、`.bmp`、`.tif`、`.tiff` |
| 动图 | `.gif` |

说明：`.doc`、`.ppt`、`.xls`、`.rtf`、`.odt`、`.ods`、`.csv` 等旧格式或非 OOXML 格式需要借助 LibreOffice 转换后再处理。

---

## 4. 水印排布方式

### checkerboard：交叉留空式排布

`checkerboard` 是推荐的视觉方案。它按照“文字槽 / 空槽”交替的方式排布水印：

```text
文字 + 横向间距 + 空槽 + 横向间距 + 文字
空槽 + 横向间距 + 文字 + 横向间距 + 空槽
文字 + 横向间距 + 空槽 + 横向间距 + 文字
```

这种排布比传统密集平铺更清爽，不容易形成明显的阶梯状视觉压迫。

示例命令：

```bash
python scripts/universal_watermark.py input.pdf \
  --text "试用水印" \
  --layout checkerboard \
  --spacing-x-font-multiplier 2.0 \
  --spacing-y-font-multiplier 3.0 \
  --empty-slot-multiplier 1.0
```

推荐参数：

```bash
--layout checkerboard
--spacing-x-font-multiplier 2.0
--spacing-y-font-multiplier 3.0
--empty-slot-multiplier 1.0
```

### staggered：传统错行平铺

`staggered` 是传统水印排布方式，每一行都有水印，奇偶行横向错开半个间距：

```bash
python scripts/universal_watermark.py input.pdf --text "试用水印" --layout staggered
```

---

## 5. 常用参数

| 参数 | 说明 | 示例 |
|---|---|---|
| `--text` | 水印文字 | `--text "试用水印"` |
| `--angle` | 水印旋转角度 | `--angle 45` |
| `--opacity` | 水印透明度，范围 `0` 到 `1` | `--opacity 0.18` |
| `--color` | 水印颜色，支持 RGB 或十六进制 | `--color "#808080"` |
| `--font-path` | 字体文件路径 | `--font-path "C:\Windows\Fonts\msyh.ttc"` |
| `--font-size-ratio` | 字号相对于页面宽度的比例 | `--font-size-ratio 0.055` |
| `--layout` | 水印排布方式 | `--layout checkerboard` |
| `--spacing-x-ratio` | 横向间距，按页面宽度比例计算 | `--spacing-x-ratio 0.32` |
| `--spacing-y-ratio` | 纵向间距，按页面高度比例计算 | `--spacing-y-ratio 0.18` |
| `--spacing-x-font-multiplier` | 横向间距，按字体行高倍数计算 | `--spacing-x-font-multiplier 2.0` |
| `--spacing-y-font-multiplier` | 纵向间距，按字体行高倍数计算 | `--spacing-y-font-multiplier 3.0` |
| `--empty-slot-multiplier` | 空槽宽度相对于文字槽宽度的倍数 | `--empty-slot-multiplier 1.0` |
| `--output-dir` | 输出目录 | `--output-dir watermarked` |
| `--suffix` | 输出文件名后缀 | `--suffix "_加水印"` |
| `--legacy-target` | 旧格式文件转换目标 | `--legacy-target editable` |
| `--excel-mode` | Excel 水印模式 | `--excel-mode background` |

---

## 6. Excel 水印模式说明

Excel 没有像 Word 那样真正的“正文后方水印层”，因此本项目提供三种实用模式：

| 模式 | 说明 | 适用场景 |
|---|---|---|
| `background` | 添加工作表背景图片 | 适合查看和编辑，不容易干扰单元格操作 |
| `overlay` | 添加透明图片浮层 | 更适合打印和导出 PDF，但可能影响单元格选择 |
| `both` | 同时使用背景和浮层 | 视觉效果最明显，但对编辑干扰最大 |

默认推荐：

```bash
--excel-mode background
```

如果需要打印或导出 PDF，建议使用：

```bash
--excel-mode overlay --opacity 0.12
```

---

## 7. 输出规则

本工具不会覆盖原文件，而是生成新文件。

示例：

```text
report.docx      -> report_加水印.docx
paper.pdf        -> paper_加水印.pdf
slides.pptx      -> slides_加水印.pptx
table.xlsx       -> table_加水印.xlsx
image.jpg        -> image_加水印.jpg
```

如果输出目录里已经存在同名文件，会自动追加编号：

```text
report_加水印.docx
report_加水印_1.docx
report_加水印_2.docx
```

---

## 8. 项目结构

```text
universal-watermark/
  SKILL.md
  README.md
  README_zh-CN.md
  scripts/
    universal_watermark.py
    watermark/
      __init__.py
      options.py
      constants.py
      common.py
      detector.py
      converters.py
      dispatcher.py
      word.py
      pdf.py
      ppt.py
      excel.py
      image.py
      gif.py
      svg.py
      cli.py
```

各模块职责如下：

| 模块 | 作用 |
|---|---|
| `universal_watermark.py` | 主入口文件 |
| `cli.py` | 命令行参数解析 |
| `dispatcher.py` | 根据文件类型分发到不同处理器 |
| `detector.py` | 文件类型识别 |
| `common.py` | 通用工具函数，包括字体、水印图层、OOXML 辅助函数 |
| `converters.py` | LibreOffice 格式转换工具 |
| `word.py` | Word / DOCX 水印处理 |
| `pdf.py` | PDF 水印处理 |
| `ppt.py` | PowerPoint / PPTX 水印处理 |
| `excel.py` | Excel / XLSX / XLSM 水印处理 |
| `image.py` | 静态图片水印处理 |
| `gif.py` | GIF 动图逐帧水印处理 |
| `svg.py` | SVG 转换后水印处理 |

---

## 9. 注意事项与限制

- `.doc`、`.ppt`、`.xls` 等旧版 Office 文件需要先转换后处理；
- LibreOffice 转换可能造成轻微版式差异；
- PDF 水印通常是覆盖在页面内容上方，建议使用较低透明度；
- Excel 的 `background` 模式通常不参与打印；
- Excel 的 `overlay` 模式更适合打印，但可能影响表格编辑；
- GIF 重新保存后可能因调色板限制产生轻微画质变化；
- 超大图片或多页 TIFF 可能占用较多内存；
- 加密 PDF 需要具备相应权限后才能处理。

---

## 10. 开发与维护

检查 Python 文件语法：

```bash
python -m compileall scripts
```

查看命令行帮助：

```bash
python scripts/universal_watermark.py --help
```

维护建议：

- 调整 Word 水印逻辑：修改 `scripts/watermark/word.py`
- 调整 PDF 水印逻辑：修改 `scripts/watermark/pdf.py`
- 调整 PowerPoint 水印逻辑：修改 `scripts/watermark/ppt.py`
- 调整 Excel 水印逻辑：修改 `scripts/watermark/excel.py`
- 调整图片水印逻辑：修改 `scripts/watermark/image.py`
- 调整 GIF 水印逻辑：修改 `scripts/watermark/gif.py`
- 调整水印排布和间距：修改 `scripts/watermark/common.py` 和 `scripts/watermark/options.py`

---

## 推荐 GitHub Topics

```text
watermark
watermark-generator
watermark-tool
python
cli
pdf-watermark
docx-watermark
pptx-watermark
excel-watermark
image-watermark
chatgpt-skill
office-automation
libreoffice
pymupdf
pillow
```

---

## 开源协议

推荐使用 MIT License。
