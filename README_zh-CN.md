# universal-watermark

[English](README.md)

![License](https://img.shields.io/github/license/czhanp/universal_watermark)
![Stars](https://img.shields.io/github/stars/czhanp/universal_watermark?style=social)
![npm](https://img.shields.io/npm/v/@czhanp/universal-watermark-skill)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

一个代码优先的多格式水印生成 **Agent Skill** 和 **Python CLI 工具**，支持 Word、PDF、PowerPoint、Excel、图片和 GIF。

`universal-watermark` 可以自动识别文件格式，选择对应处理器，添加可见文字水印，并在不覆盖原文件的前提下生成新的带水印文件。

## 为什么做这个项目？

很多水印工具只支持单一格式，例如只处理 PDF 或图片。但实际工作里，文件往往是混合的：

- Word、PDF、PPT、Excel、图片、GIF 都可能需要加水印；
- 不同格式的水印插入方式完全不同；
- 批量处理时不适合手工逐个转换；
- 原文件不能被破坏或覆盖；
- Agent / Codex / Claude Code 需要一个可以长期复用的 Skill。

本项目的目标就是把这些流程统一成一个命令和一个可复用 Skill。

## 效果预览

下图展示了本工具对 PDF、Word、图片、Excel 和 PowerPoint 文件添加水印后的效果。

<img src="example/show.png" alt="universal-watermark 效果预览" width="100%">

## 快速开始

安装 Python 依赖：

```bash
pip install pillow lxml python-docx pymupdf python-pptx
```

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

## 作为 Agent Skill 安装

本仓库可以作为本地 Skill 安装到 Codex、Claude Code 或其他 agent 的 skills 目录中。

```bash
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

默认安装到以下目录：

```text
~/.codex/skills/universal-watermark
~/.claude/skills/universal-watermark
~/.agents/skills/universal-watermark
```

也可以只安装到某一个目标：

```bash
universal-watermark-skill install --target codex
universal-watermark-skill install --target claude
universal-watermark-skill install --target agents
```

如果不想全局保留 npm 包，可以只执行一次安装器：

```bash
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

注意：npm 包主要用于分发 Skill 文件，实际水印处理逻辑仍然基于 Python，因此 Python 依赖需要单独安装。

## 支持格式

| 类型 | 支持格式 |
|---|---|
| Word | `.docx`、`.doc`、`.rtf`、`.odt` |
| PDF | `.pdf` |
| PowerPoint | `.pptx`、`.ppt` |
| Excel | `.xlsx`、`.xlsm`、`.xltx`、`.xltm`、`.xls`、`.ods`、`.csv` |
| 图片 | `.png`、`.jpg`、`.jpeg`、`.webp`、`.bmp`、`.tif`、`.tiff` |
| 动图 | `.gif` |

说明：`.doc`、`.ppt`、`.xls`、`.rtf`、`.odt`、`.ods`、`.csv` 等旧格式或非 OOXML 格式通常需要借助 LibreOffice 转换后再处理。

## 常用命令示例

### Word / DOCX

```bash
python scripts/universal_watermark.py report.docx --text "试用水印" --angle 45 --opacity 0.18
```

### PDF

```bash
python scripts/universal_watermark.py paper.pdf --text "内部资料" --opacity 0.15
```

### PowerPoint

```bash
python scripts/universal_watermark.py slides.pptx --text "草稿" --angle -45
```

### Excel

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

### 图片

```bash
python scripts/universal_watermark.py image.jpg --text "试用水印"
```

### GIF 动图

```bash
python scripts/universal_watermark.py animation.gif --text "试用水印"
```

### 旧版 Office 文件

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

## 水印排布方式

### `checkerboard`：交叉留空式排布

`checkerboard` 是推荐的视觉方案。它按照“文字槽 / 空槽”交替的方式排布水印，比传统密集平铺更清爽，不容易形成明显的阶梯状视觉压迫。

```bash
python scripts/universal_watermark.py input.pdf \
  --text "试用水印" \
  --layout checkerboard \
  --spacing-x-font-multiplier 2.0 \
  --spacing-y-font-multiplier 3.0 \
  --empty-slot-multiplier 1.0
```

### `staggered`：传统错行平铺

`staggered` 是传统水印排布方式，每一行都有水印，奇偶行横向错开半个间距。

```bash
python scripts/universal_watermark.py input.pdf --text "试用水印" --layout staggered
```

## 常用参数

| 参数 | 说明 | 示例 |
|---|---|---|
| `--text` | 水印文字 | `--text "试用水印"` |
| `--angle` | 水印旋转角度 | `--angle 45` |
| `--opacity` | 水印透明度，范围 `0` 到 `1` | `--opacity 0.18` |
| `--color` | 水印颜色，支持 RGB 或十六进制 | `--color "#808080"` |
| `--font-path` | 字体文件路径 | `--font-path "C:\Windows\Fonts\msyh.ttc"` |
| `--layout` | 水印排布方式 | `--layout checkerboard` |
| `--output-dir` | 输出目录 | `--output-dir watermarked` |
| `--suffix` | 输出文件名后缀 | `--suffix "_加水印"` |
| `--legacy-target` | 旧格式文件转换目标 | `--legacy-target editable` |
| `--excel-mode` | Excel 水印模式 | `--excel-mode background` |

使用高级参数前建议查看当前脚本帮助：

```bash
python scripts/universal_watermark.py --help
```

## Excel 水印模式说明

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

## 输出规则

本工具默认不会覆盖原文件，而是生成新文件。

```text
report.docx    -> report_加水印.docx
paper.pdf      -> paper_加水印.pdf
slides.pptx    -> slides_加水印.pptx
table.xlsx     -> table_加水印.xlsx
image.jpg      -> image_加水印.jpg
```

如果输出目录里已经存在同名文件，会自动追加编号：

```text
report_加水印.docx
report_加水印_1.docx
report_加水印_2.docx
```

## 项目结构

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

## 注意事项与限制

- `.doc`、`.ppt`、`.xls` 等旧版 Office 文件需要先转换后处理；
- LibreOffice 转换可能造成轻微版式差异；
- PDF 水印通常覆盖在页面内容上方，建议使用较低透明度；
- Excel 的 `background` 模式通常不参与打印；
- Excel 的 `overlay` 模式更适合打印，但可能影响表格编辑；
- GIF 重新保存后可能因调色板限制产生轻微画质变化；
- 超大图片或多页 TIFF 可能占用较多内存；
- 加密 PDF 需要具备相应权限后才能处理。

## 开发与维护

检查 Python 文件语法：

```bash
python -m compileall scripts
```

查看命令行帮助：

```bash
python scripts/universal_watermark.py --help
```

维护建议：

| 模块 | 作用 |
|---|---|
| `scripts/watermark/word.py` | Word / DOCX 水印处理 |
| `scripts/watermark/pdf.py` | PDF 水印处理 |
| `scripts/watermark/ppt.py` | PowerPoint / PPTX 水印处理 |
| `scripts/watermark/excel.py` | Excel / XLSX / XLSM 水印处理 |
| `scripts/watermark/image.py` | 静态图片水印处理 |
| `scripts/watermark/gif.py` | GIF 动图逐帧水印处理 |
| `scripts/watermark/common.py` | 通用水印图层、字体和 OOXML 工具 |
| `scripts/watermark/options.py` | 水印参数定义 |

## 开源协议

MIT License。
