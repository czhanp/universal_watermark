---
name: universal-watermark
description: >
  多格式文件水印处理技能。用于给 Word、PDF、PPT、Excel、图片等文件添加倾斜、平铺、
  半透明水印。当用户要求给 doc、docx、pdf、ppt、pptx、xls、xlsx、xlsm、ods、csv、png、jpg、jpeg、webp、
  bmp、tif、tiff、gif 等文件加水印，或要求自动识别文件格式后选择合适方式处理时，
  应触发本技能。技能优先保持原格式；对 .doc/.ppt/.xls 等旧版二进制 Office 格式，
  先转换为 .docx/.pptx/.xlsx 或 PDF 后再处理。
---

# 多格式文件水印处理技能

## 1. 技能目标

本技能用于给多种文件添加稳定、可控、尽量不破坏原内容的水印。

支持范围：

- Word：`.docx`、`.doc`、`.rtf`、`.odt`
- PDF：`.pdf`
- PowerPoint：`.pptx`、`.ppt`
- Excel：`.xlsx`、`.xlsm`、`.xltx`、`.xltm`、`.xls`、`.ods`、`.csv`
- 图片：`.png`、`.jpg`、`.jpeg`、`.webp`、`.bmp`、`.tif`、`.tiff`
- 动图：`.gif`

默认水印：

```yaml
text: "内部资料"
angle: 45
opacity: 0.18
color: [120, 120, 120]
font_size_ratio: 0.055
tile: true
layout: checkerboard
spacing_x_font_multiplier: 0.5
spacing_y_font_multiplier: 1.5
empty_slot_multiplier: 1.0
apply_to: all_pages_or_frames
output_suffix: "_加水印"
```

核心原则：

```text
自动识别格式
→ 根据格式选择处理路线
→ 生成带水印的新文件
→ 不覆盖原文件
→ 必要时进行格式转换并说明风险
```

---

## 2. 触发条件

用户出现以下意图时，应使用本技能：

```text
给文件加水印
给 Word 加水印
给 doc/docx 加水印
给 PDF 加水印
给 PPT/PPTX 加水印
给 Excel/XLS/XLSX 加水印
给表格/电子表格加水印
给图片加水印
给 GIF 加水印
加棱镜极智能
加草稿水印
加机密水印
加内部资料水印
添加倾斜水印
添加 45° 水印
添加平铺水印
批量给文件加水印
自动识别文件格式并加水印
```

---

## 3. 总处理规则

### 3.1 不覆盖原文件

必须输出新文件。

示例：

```text
报告.docx      → 报告_加水印.docx
论文.pdf       → 论文_加水印.pdf
演示文稿.pptx  → 演示文稿_加水印.pptx
表格.xlsx      → 表格_加水印.xlsx
图片.jpg       → 图片_加水印.jpg
```

### 3.2 自动识别格式

不能只依赖扩展名，应综合：

```text
文件扩展名
MIME / 魔数
OOXML ZIP 内部结构
OLE 复合文档文件头
```

判断规则：

```text
ZIP 包含 word/document.xml       → docx
ZIP 包含 ppt/presentation.xml    → pptx
ZIP 包含 xl/workbook.xml         → xlsx/xlsm
文件头 D0 CF 11 E0 A1 B1 1A E1  → 旧版 Office 二进制格式，结合扩展名判断 doc/ppt/xls
```

### 3.3 优先保持原格式

```text
docx → docx
pdf  → pdf
pptx → pptx
xlsx/xlsm → xlsx/xlsm
png/jpg/webp/bmp/tiff → 原图片格式
gif → gif
```

对旧格式：

```text
doc → 优先转 docx 后加水印；若失败，转 pdf 后加水印
ppt → 优先转 pptx 后加水印；若失败，转 pdf 后加水印
xls/ods/csv → 优先转 xlsx 后加水印；若失败，转 pdf 后加水印
```

必须说明：

```text
.doc/.ppt/.xls 是旧版或非 OOXML 格式，转换时可能存在轻微版式差异。
```

---

## 4. 分格式处理路线

### 4.1 DOCX

推荐路线：

```text
生成透明整页水印 PNG
→ 将 PNG 写入 word/media/
→ 修改 word/header*.xml
→ 修改 word/_rels/header*.xml.rels
→ 更新 [Content_Types].xml
→ 重新打包 docx
```

要求：

- 不在正文中反复插入水印文字；
- 尽量处理所有页眉；
- 尽量保留正文、表格、图片、样式；
- 重复运行不应无限叠加旧水印。

### 4.2 DOC / RTF / ODT

推荐路线：

```text
doc/rtf/odt → docx → DOCX 水印流程
```

如果转换失败：

```text
doc/rtf/odt → pdf → PDF 水印流程
```

依赖：

```text
LibreOffice / soffice
或 Windows + Microsoft Office COM
```

Windows 实战补充：
- 优先使用 LibreOffice/soffice 转换旧版 `.doc/.ppt`。
- 如果本机没有 LibreOffice，但安装了 Microsoft Word 或 WPS，可用 `pywin32` 通过 `Word.Application` / WPS 兼容 COM 先把 `.doc` 转成 `.docx`，再调用本脚本加水印。
- WPS/Word COM 自动化可能需要桌面权限，适合 Windows 本机批处理；服务器或无桌面环境仍建议安装 LibreOffice。

### 4.3 PDF

推荐路线：

```text
PyMuPDF 打开 PDF
→ 每页生成同尺寸透明水印 PNG
→ insert_image 叠加到页面
→ 保存新 PDF
```

注意：

- PDF 没有 Word 那样的页眉层；
- 水印通常是叠加到页面内容上方；
- 因此透明度应较低，避免遮挡正文；
- 加密 PDF 需要密码或权限。

### 4.4 PPTX

推荐路线：

```text
python-pptx 打开演示文稿
→ 生成与幻灯片同尺寸的透明水印 PNG
→ 每页 slide 添加水印图片
→ 尽量将水印 shape 移到图层底部
→ 保存新 pptx
```

注意：

- 如果无法保证底层，使用较低透明度；
- 若用户更重视发布效果而非可编辑性，可转 PDF 后加水印。

### 4.5 PPT

推荐路线：

```text
ppt → pptx → PPTX 水印流程
```

如果转换失败：

```text
ppt → pdf → PDF 水印流程
```


### 4.6 Excel / XLSX / XLSM

推荐路线：

```text
直接修改 Excel OOXML 包结构
→ 为每个工作表生成透明水印 PNG
→ 根据模式写入 worksheet background picture 或 drawing 浮层
→ 更新工作表 rels、drawing rels、media 和 [Content_Types].xml
→ 重新打包 xlsx/xlsm
```

Excel 特别说明：

```text
Excel 没有完全等同于 Word 的“正文后方水印层”。
因此本技能提供两种实现模式：
```

- `background`：写入工作表背景图片，水印位于单元格后方，不影响编辑和选择单元格，但通常不参与打印；
- `overlay`：插入透明图片浮层，视觉效果更明显，也更可能随打印/导出出现，但会覆盖在单元格上方，应使用较低透明度；
- `both`：同时添加背景和浮层，视觉最强，但对编辑干扰最大，只在用户明确需要时使用。

默认推荐：

```text
--excel-mode background
```

需要打印或导出 PDF 时，可使用：

```text
--excel-mode overlay
```

要求：

- `.xlsx/.xlsm` 可直接处理；
- `.xls/.ods/.csv` 应先转为 `.xlsx` 或 `.pdf` 后处理；
- `.xlsm` 处理时应尽量保留宏相关文件，不主动删除 vbaProject；
- 不应使用会破坏公式、样式和工作表结构的方式重写表格内容；
- 背景模式可能替换原有工作表背景图片；
- 浮层模式应尽量估算已使用区域并覆盖主要数据区域。

### 4.7 XLS / ODS / CSV

推荐路线：

```text
xls/ods/csv → xlsx → Excel 水印流程
```

如果转换失败：

```text
xls/ods/csv → pdf → PDF 水印流程
```

注意：

- `.xls` 是旧版二进制 Excel 格式，不应按 `.xlsx` 的 XML 方法直接处理；
- `.csv` 本身没有工作簿样式、图片和水印层，必须转为 `.xlsx` 或 `.pdf` 后才能加水印；
- 转换可能造成列宽、字体、分页和公式兼容差异。

### 4.8 图片

推荐路线：

```text
Pillow 打开图片
→ 修正 EXIF 方向
→ 生成同尺寸透明水印层
→ alpha 合成
→ 按合适格式保存
```

注意：

- JPEG 不支持透明通道，最终需转 RGB；
- TIFF 可能是多页图，应逐页处理；
- 大图注意内存。

### 4.9 GIF

推荐路线：

```text
读取所有帧
→ 每帧合成水印
→ 保留 duration/loop
→ 保存新 GIF
```

注意：

- GIF 调色板有限，重新保存可能有轻微画质损失；
- 若用户只需要静态图，可输出首帧 PNG。

---

## 5. 推荐依赖

Python 依赖：

```bash
pip install pillow lxml python-docx pymupdf python-pptx
```

可选：

```bash
pip install python-magic cairosvg pillow-heif
```

Windows 可选依赖（用于 Word/WPS/Excel/PowerPoint COM 兜底转换旧版 `.doc/.ppt/.xls`）：

```bash
pip install pywin32
```

外部转换工具：

```text
LibreOffice / soffice
```

---

## 6. 推荐文件结构

```text
universal-watermark/
  SKILL.md
  README.md
  scripts/
    universal_watermark.py          # 命令行入口，只负责启动
    watermark/
      __init__.py
      options.py                    # 水印参数 dataclass
      constants.py                  # OOXML 命名空间、支持格式集合
      common.py                     # 通用工具：字体、水印图层、OOXML rels 等
      detector.py                   # 文件格式识别
      converters.py                 # LibreOffice 转换
      dispatcher.py                 # 按格式分发到各处理器
      word.py                       # DOCX 水印处理
      pdf.py                        # PDF 水印处理
      ppt.py                        # PPTX 水印处理
      excel.py                      # XLSX/XLSM 水印处理
      image.py                      # 静态图片水印处理
      gif.py                        # GIF 逐帧水印处理
      svg.py                        # SVG 转 PNG 后水印处理
```

---

## 7. 推荐使用命令

单文件：

```bash
python scripts/universal_watermark.py input.docx --text "棱镜极智能" --angle 45
```

多个文件：

```bash
python scripts/universal_watermark.py a.docx b.pdf c.pptx table.xlsx image.jpg --output-dir output --text "内部资料"
```

中文水印建议显式指定中文字体，避免缺字或显示成方块：

```bash
python scripts/universal_watermark.py input.pdf --output-dir output --text "棱镜极智能" --font-path "C:\Windows\Fonts\msyh.ttc" --angle 45
```



水印排布默认使用交叉留空式 `checkerboard`：

```text
第 1 行：文字 + 横向间距 + 空槽 + 横向间距 + 文字 ...
第 2 行：空槽 + 横向间距 + 文字 + 横向间距 + 空槽 ...
第 3 行：重复第 1 行
```

可通过以下参数调节：

```bash
# 横向间距 = 字体行高 × 0.5
python scripts/universal_watermark.py input.pdf --text "棱镜极智能" --spacing-x-font-multiplier 0.5

# 纵向行距 = 字体行高 × 1.5
python scripts/universal_watermark.py input.pdf --text "棱镜极智能" --spacing-y-font-multiplier 1.5

# 空槽宽度 = 文字槽宽度 × 1.2
python scripts/universal_watermark.py input.pdf --text "棱镜极智能" --empty-slot-multiplier 1.2

# 如需使用旧版错行平铺
python scripts/universal_watermark.py input.pdf --text "棱镜极智能" --layout staggered
```

Excel 默认使用工作表背景水印，不影响单元格编辑：

```bash
python scripts/universal_watermark.py table.xlsx --output-dir output --text "棱镜极智能" --excel-mode background
```

如果希望水印更可能参与打印或导出 PDF，可使用透明浮层模式：

```bash
python scripts/universal_watermark.py table.xlsx --output-dir output --text "棱镜极智能" --excel-mode overlay --opacity 0.12
```

同时添加背景和浮层：

```bash
python scripts/universal_watermark.py table.xlsx --output-dir output --text "棱镜极智能" --excel-mode both --opacity 0.10
```

批量处理时建议始终指定单独输出目录，例如 `--output-dir watermarked`，避免和原文件混在一起。若输出目录中已有同名结果，脚本会自动追加 `_1`、`_2` 等编号，不会覆盖已有文件。

旧版 Office 文件：

```bash
python scripts/universal_watermark.py old.doc --legacy-target editable
```

如果没有 LibreOffice，可先用 Word/WPS COM 将旧版 `.doc` 转为临时 `.docx`，再执行：

```bash
python scripts/universal_watermark.py converted.docx --output-dir output --text "棱镜极智能" --font-path "C:\Windows\Fonts\msyh.ttc"
```

如果只需要发布版：

```bash
python scripts/universal_watermark.py old.doc --legacy-target pdf
```

---

## 8. 必须验证

处理完成后应尽量检查：

```text
输出文件是否生成
输出文件是否非空
页数/幻灯片数/工作表数/帧数是否基本一致
水印是否可见
水印是否倾斜
水印是否平铺
水印是否过深
主体内容是否被严重遮挡
```

对于 Word/PPT/PDF，如条件允许，应渲染首页或打开检查。

---

## 9. 禁止事项

不得：

```text
覆盖原文件
将水印作为普通正文插入导致排版改变
把 .doc 当作 .docx 直接改 XML
把 .ppt 当作 .pptx 直接改 XML
把 .xls 当作 .xlsx 直接改 XML
声称处理成功但没有输出文件
忽略旧格式转换风险
忽略中文字体缺失问题
让水印过深影响阅读
```

---

## 10. 回复用户格式

处理完成后，应回复：

```text
已完成水印处理。

识别到的文件格式：xxx
采用的处理路线：xxx
水印文字：xxx
水印角度：xx°
水印透明度：xx
输出文件：xxx

说明：如果原文件为 .doc/.ppt/.xls/.ods/.csv 等旧格式，已转换为 xxx 后处理，可能存在轻微版式差异。
```

---

## 11. 技能总结

本技能不是单一 Word 水印工具，而是多格式水印调度器。

核心思想：

```text
先识别格式
再选择路线
能原生处理就原生处理
不能原生处理就转换处理
转换仍失败就 PDF 兜底
始终保留原文件
始终输出新文件
```

推荐路线：

```text
docx → 直接改 OOXML
doc/rtf/odt → 转 docx 或 pdf
pdf → PyMuPDF 逐页加水印
pptx → python-pptx 每页加水印
ppt → 转 pptx 或 pdf
xlsx/xlsm → 直接改 Excel OOXML，添加背景或浮层水印
xls/ods/csv → 转 xlsx 或 pdf
图片 → Pillow 合成水印
gif → Pillow 逐帧加水印
```

