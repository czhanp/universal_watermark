#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多格式水印工具入口文件。

这个文件只负责启动命令行程序，具体格式处理逻辑位于 scripts/watermark/ 下的各模块中。
"""

from watermark.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
