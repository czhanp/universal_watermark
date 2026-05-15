# universal-watermark 今日工作复盘最终整理版

## 目录

- [0. 最终结论](#0-最终结论)
- [1. 项目基本信息](#1-项目基本信息)
- [2. 一条最标准的操作顺序](#2-一条最标准的操作顺序)
- [3. 项目发布前应该准备哪些文件](#3-项目发布前应该准备哪些文件)
- [4. package.json 应该怎么理解](#4-packagejson-应该怎么理解)
- [5. bin/install.js 的作用](#5-bininstalljs-的作用)
- [6. .gitignore 与 .npmignore](#6-gitignore-与-npmignore)
- [7. README 与效果图整理](#7-readme-与效果图整理)
- [8. MIT License 应该怎么加](#8-mit-license-应该怎么加)
- [9. GitHub 上传完整流程](#9-github-上传完整流程)
- [10. GitHub CLI 登录与代理问题](#10-github-cli-登录与代理问题)
- [11. Git 常见问题处理](#11-git-常见问题处理)
- [12. npm 发布前本地检查](#12-npm-发布前本地检查)
- [13. npm 发布流程](#13-npm-发布流程)
- [14. npm 2FA / Security Key 问题复盘](#14-npm-2fa--security-key-问题复盘)
- [15. 发布后检查](#15-发布后检查)
- [16. 用户安装和验证](#16-用户安装和验证)
- [17. npx / bin 入口问题复盘](#17-npx--bin-入口问题复盘)
- [18. 常用命令速查表](#18-常用命令速查表)
- [19. 下次第一次上传新项目的行动清单](#19-下次第一次上传新项目的行动清单)
- [20. 下次更新项目并重新发布 npm 的行动清单](#20-下次更新项目并重新发布-npm-的行动清单)
- [21. 最后记忆版：遇到问题先看这里](#21-最后记忆版遇到问题先看这里)
- [22. 学习这些命令的方式](#22-学习这些命令的方式)

---

## 0. 最终结论

本次项目的目标不是单纯把代码上传到 GitHub，而是完成一条完整发布链路：

```text
本地 universal-watermark 项目
→ 整理为 Git 仓库
→ 上传到 GitHub
→ 配置 npm 包
→ 发布到 npm
→ 用户通过 npm / npm exec 安装为本地 Skill
→ Codex / Claude Code / agents 扫描并使用该 Skill
```

本次最终推荐的用户安装方式是：

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

也可以不保留全局 npm 包，只执行一次安装：

```powershell
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

不建议把下面这种旧写法作为主推荐：

```powershell
npx @czhanp/universal-watermark-skill universal-watermark
```

原因是：在 Windows / npm / npx 的某些组合下，短写命令可能不能正确解析包内 `bin` 入口。

---

## 1. 项目基本信息

### 1.1 本地项目目录

```powershell
C:\Users\walke\Desktop\ALL\universal-watermark
```

### 1.2 GitHub 仓库

最终使用的仓库地址：

```text
https://github.com/czhanp/universal_watermark
```

如果本地远程地址曾经是旧账号或旧仓库，需要用 `git remote set-url` 改回来。

### 1.3 npm 包名

```text
@czhanp/universal-watermark-skill
```

这是一个 scoped package，也就是带作用域的 npm 包。

结构含义：

```text
@czhanp                         = npm scope / 用户或组织命名空间
universal-watermark-skill       = 包名
```

### 1.4 npm 包的真实定位

这个项目本体是 Python Skill，不是 Node.js 库。

npm 包在这里主要起“分发器”和“安装器”的作用：

```text
通过 npm 下载 Skill 文件
通过 bin/install.js 把 Skill 安装到本机 agent skills 目录
让 Codex、Claude Code、其他 agent 可以长期扫描和使用该 Skill
```

所以用户安装 npm 包之后，不是为了调用 JavaScript API，而是为了把 Skill 文件复制到这些目录：

```text
%USERPROFILE%\.codex\skills\universal-watermark
%USERPROFILE%\.claude\skills\universal-watermark
%USERPROFILE%\.agents\skills\universal-watermark
```

---

## 2. 一条最标准的操作顺序

下次做类似项目时，建议严格按照这个顺序走，不要一上来就发布 npm。

```text
1. 整理本地项目文件
2. 配置 .gitignore / .npmignore
3. 补齐 README、SKILL.md、LICENSE、package.json、bin/install.js
4. 本地测试 Python CLI 和 npm 安装器
5. GitHub 登录与代理检查
6. Git 初始化 / 远程仓库绑定 / 提交 / 推送
7. npm 登录与 registry 检查
8. npm pack --dry-run 检查打包内容
9. npm publish 发布
10. npm view 查询发布结果
11. 全局安装或 npm exec 安装验证
```

可以把它理解成：

```text
先保证项目是干净的
再保证 GitHub 上是对的
最后才发 npm
```

---

## 3. 项目发布前应该准备哪些文件

### 3.1 推荐目录结构

```text
universal-watermark/
  SKILL.md
  README.md
  README_zh-CN.md
  LICENSE
  package.json
  .gitignore
  .npmignore
  bin/
    install.js
  scripts/
    universal_watermark.py
    watermark/
      ...
  example/
    show.png
```

其中：

| 文件 / 目录 | 作用 |
|---|---|
| `SKILL.md` | Skill 的核心说明文件，供 agent 理解何时调用该 Skill |
| `README.md` | 英文项目说明，给 GitHub / npm 用户阅读 |
| `README_zh-CN.md` | 中文项目说明 |
| `LICENSE` | 开源协议文件 |
| `package.json` | npm 发布配置 |
| `.gitignore` | 控制哪些文件不要进入 Git 仓库 |
| `.npmignore` | 控制哪些文件不要进入 npm 包 |
| `bin/install.js` | npm 包暴露出的命令入口 |
| `scripts/` | Python 水印处理代码 |
| `example/show.png` | README 效果预览图 |

---

## 4. package.json 应该怎么理解

`package.json` 是 npm 发布必须使用的包描述文件。

本项目推荐的关键字段如下：

```json
{
  "name": "@czhanp/universal-watermark-skill",
  "version": "0.1.1",
  "license": "MIT",
  "publishConfig": {
    "access": "public"
  },
  "bin": {
    "universal-watermark-skill": "bin/install.js"
  },
  "files": [
    "bin/",
    "SKILL.md",
    "README.md",
    "README_zh-CN.md",
    "LICENSE",
    "scripts/",
    "!scripts/**/__pycache__/**",
    "!scripts/**/*.pyc",
    "!scripts/**/*.pyc.*",
    "example/",
    "examples/"
  ]
}
```

### 4.1 字段含义

| 字段 | 含义 |
|---|---|
| `name` | npm 包名，发布后用户通过这个名字安装 |
| `version` | npm 版本号，同一个包不能重复发布相同版本 |
| `license` | 开源协议，本项目使用 MIT |
| `publishConfig.access` | 让 scoped package 以 public 方式发布 |
| `bin` | 定义安装后可执行的命令 |
| `files` | npm 发布白名单，控制哪些文件会被打进 npm 包 |

### 4.2 为什么 scoped package 要注意 public

包名是：

```text
@czhanp/universal-watermark-skill
```

这种以 `@用户名/包名` 形式命名的 npm 包叫 scoped package。

scoped package 发布时，如果想公开给所有人使用，需要显式声明 public：

```json
"publishConfig": {
  "access": "public"
}
```

发布时也可以再写一遍：

```powershell
npm publish --access public
```

这样更保险。

---

## 5. bin/install.js 的作用

`bin/install.js` 是 npm 包安装后暴露给用户的命令入口。

用户执行：

```powershell
universal-watermark-skill install --all
```

实际上就是 npm 找到 `package.json` 里的 `bin` 配置，然后运行：

```text
bin/install.js
```

### 5.1 安装器支持的主要命令

```powershell
universal-watermark-skill install --all
universal-watermark-skill install --target codex
universal-watermark-skill install --target claude
universal-watermark-skill install --target agents
universal-watermark-skill download universal-watermark
```

### 5.2 命令含义

| 命令 | 含义 |
|---|---|
| `install --all` | 安装到所有支持的 agent Skill 目录 |
| `install --target codex` | 只安装到 Codex Skill 目录 |
| `install --target claude` | 只安装到 Claude Code Skill 目录 |
| `install --target agents` | 只安装到通用 agents Skill 目录 |
| `download universal-watermark` | 只复制一份本地 Skill 目录，不写入全局 agent 目录 |

### 5.3 安装器应该复制哪些文件

```text
SKILL.md
README.md
README_zh-CN.md
LICENSE
scripts/
example/
examples/，如果存在
```

### 5.4 安装器应该跳过哪些文件

```text
__pycache__/
*.pyc
*.pyc.*
.git/
node_modules/
.env
```

这些文件要么是缓存，要么是本地环境文件，不应该出现在最终安装结果里。

---

## 6. .gitignore 与 .npmignore

### 6.1 .gitignore 的作用

`.gitignore` 用来告诉 Git：

```text
这些文件不要加入版本管理
```

适合忽略：

```text
Python 缓存
虚拟环境
本地配置
npm 依赖
npm 打包产物
系统临时文件
```

推荐内容：

```gitignore
__pycache__/
*.py[cod]
*$py.class

.venv/
venv/
.env

node_modules/
*.tgz
npm-debug.log*

.DS_Store
Thumbs.db
```

### 6.2 .npmignore 的作用

`.npmignore` 用来告诉 npm：

```text
这些文件不要发布到 npm 包里
```

推荐内容：

```gitignore
__pycache__/
*.py[cod]
node_modules/
*.tgz
npm-debug.log*
.env
.venv/
venv/
.git/
```

### 6.3 .gitignore 和 .npmignore 的区别

| 文件 | 控制对象 | 影响范围 |
|---|---|---|
| `.gitignore` | Git 仓库 | 是否上传到 GitHub |
| `.npmignore` | npm 包 | 是否发布到 npm |

注意：如果 `package.json` 中已经写了 `files` 字段，npm 会优先按 `files` 白名单打包，`.npmignore` 主要作为辅助保险。

---

## 7. README 与效果图整理

### 7.1 README 推荐顺序

英文 README：

```text
# universal-watermark
项目一句话介绍
项目简短说明

## Preview

## 1. Skill Usage
## 2. CLI Usage
## 3. Installation
## 4. Examples
```

中文 README：

```text
# universal-watermark
项目一句话介绍
项目简短说明

## 效果预览

## 1. Skill 使用说明
## 2. CLI 使用方法
## 3. 安装方法
## 4. 示例
```

学习上更顺的逻辑是：

```text
先告诉别人这是什么
再让别人看到效果
然后再告诉别人怎么用
```

### 7.2 README 中插入图片

如果图片位置是：

```text
example/show.png
```

README 写：

```html
<img src="example/show.png" alt="universal-watermark preview" width="100%">
```

中文 README 写：

```html
<img src="example/show.png" alt="universal-watermark 效果预览" width="100%">
```

### 7.3 图片不显示的常见原因

最常见原因是路径写错。

例如真实路径是：

```text
example/show.png
```

但 README 写成：

```text
examples/show.png
```

就会因为多了一个 `s` 而找不到图片。

解决方式二选一：

```text
1. 把 README 里的路径改成 example/show.png
2. 把文件夹从 example 改名为 examples
```

GitHub 对路径大小写敏感，所以大小写也要完全一致。

---

## 8. MIT License 应该怎么加

### 8.1 LICENSE 文件放哪里

放在仓库根目录：

```text
universal-watermark/
  LICENSE
  README.md
  SKILL.md
  scripts/
```

不要放在 `scripts/` 里，也不建议命名为：

```text
LICENSE.txt
MIT_LICENSE.md
```

标准文件名通常就是：

```text
LICENSE
```

### 8.2 PowerShell 创建 LICENSE

```powershell
@"
MIT License

Copyright (c) 2026 universal-watermark contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the `"Software`"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED `"AS IS`", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Set-Content -Encoding UTF8 LICENSE
```

### 8.3 命令解释

| 命令片段 | 含义 |
|---|---|
| `@" ... "@` | PowerShell 的多行字符串 |
| `Set-Content` | 把内容写入文件 |
| `-Encoding UTF8` | 使用 UTF-8 编码 |
| `LICENSE` | 输出文件名 |

---

## 9. GitHub 上传完整流程

### 9.1 进入项目目录

```powershell
cd "C:\Users\walke\Desktop\ALL\universal-watermark"
```

含义：

```text
进入本地项目所在文件夹。
后续 git / npm 命令都应该在这个目录里执行。
```

### 9.2 查看当前 Git 状态

```powershell
git status
```

含义：

```text
查看当前有哪些文件被修改、新增、删除，以及是否已经加入暂存区。
```

常见状态：

| 状态 | 含义 |
|---|---|
| `Untracked files` | Git 还没管理的新文件 |
| `Changes not staged` | 文件改了，但还没 `git add` |
| `Changes to be committed` | 已经 `git add`，等待 `commit` |
| `nothing to commit, working tree clean` | 工作区干净，没有要提交的内容 |

### 9.3 初始化 Git 仓库

如果项目还不是 Git 仓库：

```powershell
git init
```

含义：

```text
把当前文件夹变成 Git 仓库。
```

执行后会生成隐藏目录：

```text
.git/
```

`.git/` 里面保存版本记录、分支、远程仓库配置等信息。

### 9.4 设置主分支为 main

```powershell
git branch -M main
```

含义：

```text
把当前分支强制重命名为 main。
```

为什么要这样：

```text
GitHub 现在默认主分支通常叫 main，本地和远程统一叫 main，后续推送更省事。
```

### 9.5 添加远程仓库

如果还没有远程仓库：

```powershell
git remote add origin https://github.com/czhanp/universal_watermark.git
```

含义：

```text
给本地仓库添加一个叫 origin 的远程 GitHub 地址。
```

其中：

```text
origin = Git 默认常用远程仓库别名
```

以后执行：

```powershell
git push origin main
```

意思就是：

```text
把本地 main 分支推送到 origin 对应的 GitHub 仓库。
```

### 9.6 修改远程仓库地址

如果远程地址写错，或仓库从旧账号迁移到了新账号：

```powershell
git remote set-url origin https://github.com/czhanp/universal_watermark.git
```

含义：

```text
把 origin 绑定的远程仓库地址改成新的 GitHub 仓库地址。
```

### 9.7 查看远程仓库地址

```powershell
git remote -v
```

含义：

```text
查看当前本地仓库绑定的远程地址。
```

输出示例：

```text
origin  https://github.com/czhanp/universal_watermark.git (fetch)
origin  https://github.com/czhanp/universal_watermark.git (push)
```

其中：

```text
fetch = 拉取代码时使用的地址
push  = 推送代码时使用的地址
```

### 9.8 添加文件到暂存区

```powershell
git add .
```

含义：

```text
把当前目录下所有新增和修改的文件加入暂存区。
```

可以把它理解为：

```text
把这次准备提交的文件先装进箱子。
```

如果要把删除文件也完整加入暂存区，推荐：

```powershell
git add -A
```

`git add .` 有时对删除文件的处理不如 `git add -A` 完整。

### 9.9 提交版本

```powershell
git commit -m "Initial release"
```

含义：

```text
把暂存区中的内容保存成一次 Git 提交。
```

`-m` 后面是提交说明。

示例：

```powershell
git commit -m "Add universal watermark skill"
git commit -m "Update README with npm usage"
git commit -m "Fix npm bin entry"
git commit -m "Add MIT license"
```

可以把它理解成：

```text
git add    = 装箱
git commit = 封箱并贴标签
```

### 9.10 推送到 GitHub

第一次推送：

```powershell
git push -u origin main
```

含义：

```text
把本地 main 分支推送到 GitHub 的 main 分支。
```

其中：

| 部分 | 含义 |
|---|---|
| `git push` | 推送 |
| `-u` | 设置 upstream，上游分支 |
| `origin` | 远程仓库别名 |
| `main` | 要推送的分支 |

设置 `-u` 之后，以后可以直接：

```powershell
git push
```

不必每次写完整命令。

---

## 10. GitHub CLI 登录与代理问题

### 10.1 检查 GitHub CLI 登录状态

```powershell
gh auth status
```

含义：

```text
检查当前 GitHub CLI 是否已经登录。
```

如果出现：

```text
Token in keyring is invalid
```

说明之前保存的登录 token 已经过期、损坏或不可用，需要重新登录。

### 10.2 退出旧登录

```powershell
gh auth logout -h github.com
```

含义：

```text
退出 github.com 的 GitHub CLI 登录状态。
```

如果要指定用户：

```powershell
gh auth logout -h github.com -u walkaloner
```

### 10.3 使用浏览器登录 GitHub CLI

```powershell
gh auth login -h github.com -p https -w
```

含义：

| 参数 | 含义 |
|---|---|
| `gh auth login` | 登录 GitHub CLI |
| `-h github.com` | 指定登录 GitHub 主站 |
| `-p https` | Git 操作使用 HTTPS 协议 |
| `-w` | 使用浏览器 Web 登录 |

如果想自动复制验证码：

```powershell
gh auth login -h github.com -p https -w --clipboard
```

### 10.4 Clash 代理临时设置

如果浏览器能访问 GitHub，但 PowerShell 里的 `gh` / `git` 访问失败，可以设置临时代理：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
$env:ALL_PROXY="socks5://127.0.0.1:7890"
```

含义：

| 环境变量 | 含义 |
|---|---|
| `HTTP_PROXY` | HTTP 请求走哪个代理 |
| `HTTPS_PROXY` | HTTPS 请求走哪个代理 |
| `ALL_PROXY` | 尽量让所有协议走这个代理 |
| `127.0.0.1` | 本机 |
| `7890` | Clash 常见 Mixed Port / HTTP Port |

注意：

```text
这些命令只对当前 PowerShell 窗口有效，关闭窗口后失效。
如果你的 Clash 端口不是 7890，要改成实际端口。
```

### 10.5 给 Git 配置全局代理

```powershell
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

含义：

```text
让 Git 的 HTTP / HTTPS 请求通过 Clash 代理。
```

检查配置：

```powershell
git config --global --get http.proxy
git config --global --get https.proxy
```

取消配置：

```powershell
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 10.6 检查 github.com 是否被错误解析

```powershell
Resolve-DnsName github.com
```

含义：

```text
查看 github.com 被解析到了哪个 IP。
```

如果结果中出现：

```text
127.0.0.1
```

说明解析异常，可能是 hosts 文件写错。

### 10.7 测试 GitHub 443 端口

```powershell
Test-NetConnection github.com -Port 443
```

含义：

```text
测试本机是否能连接 GitHub 的 HTTPS 端口。
```

正常结果应该包含：

```text
TcpTestSucceeded : True
```

### 10.8 检查 hosts 文件

```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```

检查是否有：

```text
127.0.0.1 github.com
127.0.0.1 api.github.com
127.0.0.1 raw.githubusercontent.com
```

如果有，应删除或注释：

```text
# 127.0.0.1 github.com
```

修改后刷新 DNS：

```powershell
ipconfig /flushdns
```

含义：

```text
清理 Windows DNS 缓存，让 hosts 修改尽快生效。
```

---

## 11. Git 常见问题处理

### 11.1 `LF will be replaced by CRLF`

现象：

```text
warning: LF will be replaced by CRLF
```

含义：

```text
当前文件使用 LF 换行符，Git for Windows 可能会在之后把它转换为 CRLF。
```

解释：

| 换行符 | 常见系统 |
|---|---|
| `LF` | Linux / macOS |
| `CRLF` | Windows |

这个通常不是错误，可以继续提交。

如果想规范化换行，可以增加 `.gitattributes`：

```gitattributes
* text=auto

*.py text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.sh text eol=lf

*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
```

### 11.2 误提交了 `__pycache__`

`__pycache__` 和 `.pyc` 是 Python 自动生成的缓存文件，不应该上传 GitHub。

原因：

```text
1. 它们不是源码；
2. 不同 Python 版本会生成不同 pyc；
3. 会让仓库混乱；
4. 对别人使用项目没有帮助。
```

如果还没有被 Git 追踪，写 `.gitignore` 即可。

如果已经被 Git 追踪，需要执行：

```powershell
git rm -r --cached scripts/watermark/__pycache__
```

含义：

| 命令片段 | 含义 |
|---|---|
| `git rm` | 从 Git 管理中移除 |
| `-r` | 递归处理整个文件夹 |
| `--cached` | 只从 Git 版本管理中移除，不删除本地文件 |
| `scripts/watermark/__pycache__` | 要移除的缓存目录 |

检查是否仍被跟踪：

```powershell
git ls-files | findstr __pycache__
git ls-files | findstr ".pyc"
```

没有输出，说明清理干净。

### 11.3 修改上一次提交

如果刚提交完又发现漏加了 `.gitignore` 或需要移除缓存文件，可以先修改文件并 `git add`，然后执行：

```powershell
git commit --amend --no-edit
```

含义：

```text
把当前暂存区里的变化合并进上一个 commit，并保持原提交说明不变。
```

适用场景：

```text
刚提交完，马上发现一点小问题；
还没有推送到远程；
希望 Git 历史更干净。
```

如果已经推送到远程，再 amend 后通常需要：

```powershell
git push --force-with-lease
```

### 11.4 推送时报 `fetch first`

现象：

```text
! [rejected] main -> main (fetch first)
Updates were rejected because the remote contains work that you do not have locally.
```

含义：

```text
远程 GitHub 仓库里有本地没有的提交，Git 不敢直接覆盖远程内容。
```

常见原因：

```text
1. 你在 GitHub 网页上创建了 README；
2. 你在 GitHub 网页上新增了 LICENSE；
3. 你曾经清空仓库，但那个清空操作本身也产生了 commit；
4. 远程仓库初始化时自带提交，本地没有同步。
```

推荐处理方式：

```powershell
git pull --rebase origin main
git push
```

含义：

```text
先把远程提交拉下来，再把本地提交接在远程提交之后。
```

如果确认远程内容可以被本地覆盖，可以用：

```powershell
git fetch origin main
git push -u origin main --force-with-lease
```

### 11.5 `--force-with-lease` 报 `stale info`

现象：

```text
stale info
```

含义：

```text
本地没有最新的远程引用信息，Git 不知道远程现在到底是什么状态，所以拒绝安全强推。
```

处理：

```powershell
git fetch origin main
git push -u origin main --force-with-lease
```

### 11.6 `--force-with-lease` 和 `--force` 区别

| 命令 | 含义 | 风险 |
|---|---|---|
| `git push --force` | 直接强制覆盖远程 | 风险高，可能覆盖别人提交 |
| `git push --force-with-lease` | 先确认远程仍是你以为的状态，再覆盖 | 相对安全 |

优先使用：

```powershell
git push --force-with-lease
```

不要轻易使用：

```powershell
git push --force
```

---

## 12. npm 发布前本地检查

### 12.1 检查 Node.js 和 npm

```powershell
node --version
npm --version
```

含义：

```text
确认本机已经安装 Node.js 和 npm。
```

本次环境中看到过的版本示例：

```text
node v24.x
npm 11.x
```

版本号不是必须完全一样，只要 npm 功能正常即可。

### 12.2 检查 npm 登录用户

```powershell
npm whoami
```

含义：

```text
查看当前 npm CLI 登录的是哪个账号。
```

期望输出：

```text
czhanp
```

如果未登录，会提示需要认证。

### 12.3 npm 浏览器登录

```powershell
npm login --auth-type=web
```

含义：

```text
通过浏览器完成 npm 登录。
```

适合处理：

```text
npm 账号登录
2FA 验证
Security Key
Windows Hello
浏览器授权 CLI
```

普通登录也可以：

```powershell
npm login
```

但遇到 Security Key / Passkey 时，浏览器登录通常更清楚。

### 12.4 退出 npm 登录

```powershell
npm logout
```

含义：

```text
退出当前 npm CLI 登录状态。
```

如果出现：

```text
ENEEDAUTH
need auth not logged in
```

说明当前本来就没有有效登录状态，不是严重错误。

### 12.5 检查 npm registry

```powershell
npm config get registry
```

含义：

```text
查看当前 npm 从哪个 registry 查询和发布包。
```

推荐结果：

```text
https://registry.npmjs.org/
```

如果不是官方源，可以设置回官方：

```powershell
npm config set registry https://registry.npmjs.org/
```

### 12.6 检查 package.json

```powershell
node -e "const p=require('./package.json'); console.log(p.name, p.version, p.bin['universal-watermark-skill'])"
```

含义：

```text
用 Node.js 读取 package.json，确认包名、版本号、bin 入口是否正确。
```

期望输出类似：

```text
@czhanp/universal-watermark-skill 0.1.1 bin/install.js
```

### 12.7 测试安装器帮助

```powershell
node bin/install.js --help
```

含义：

```text
确认 bin/install.js 可以被 Node 执行，并且帮助信息正常。
```

### 12.8 测试 download 模式

```powershell
node bin/install.js download npm-download-test
python npm-download-test\scripts\universal_watermark.py --help
```

含义：

```text
先模拟用户下载一份本地 Skill 目录；
再验证下载出来的 Python CLI 能正常运行。
```

### 12.9 用临时 root 测试全局安装模式

```powershell
node bin/install.js install --all --root npm-global-root-test
```

含义：

```text
不直接写入真实用户目录，而是用临时目录模拟安装。
```

会模拟生成：

```text
npm-global-root-test\.codex\skills\universal-watermark
npm-global-root-test\.claude\skills\universal-watermark
npm-global-root-test\.agents\skills\universal-watermark
```

这样可以在发布前发现安装器复制文件是否正确。

### 12.10 模拟 npm 打包

```powershell
npm pack --dry-run
```

含义：

```text
模拟 npm 打包，但不真正发布。
```

它会显示 npm 最终会上传哪些文件。

重点检查不要包含：

```text
__pycache__/
*.pyc
.env
.venv/
node_modules/
.git/
临时测试输出目录
```

---

## 13. npm 发布流程

### 13.1 确认当前目录

```powershell
cd "C:\Users\walke\Desktop\ALL\universal-watermark"
```

### 13.2 确认登录

```powershell
npm whoami
```

期望输出：

```text
czhanp
```

### 13.3 检查打包内容

```powershell
npm pack --dry-run
```

确认文件清单无误后再发布。

### 13.4 发布 public scoped package

```powershell
npm publish --access public
```

含义：

| 命令片段 | 含义 |
|---|---|
| `npm publish` | 发布当前目录为 npm 包 |
| `--access public` | scoped package 按公开包发布 |

如果 npm 要求 2FA，一般需要加 OTP：

```powershell
npm publish --access public --otp=你的npm验证码
```

注意：

```text
这里需要的是 npm 账号的 2FA，不是 GitHub 的验证码。
```

### 13.5 版本号不能重复

npm 不允许重复发布同一个：

```text
name + version
```

如果已经发布过：

```text
@czhanp/universal-watermark-skill@0.1.0
```

就不能再次发布 `0.1.0`。

可以升级 patch 版本：

```powershell
npm version patch
```

含义：

```text
自动把 package.json 中的版本号从 0.1.0 改为 0.1.1，并生成一次 Git 提交 / tag。
```

语义化版本理解：

| 类型 | 示例 | 适用情况 |
|---|---|---|
| patch | `0.1.0 -> 0.1.1` | 修 bug、小改动 |
| minor | `0.1.0 -> 0.2.0` | 增加功能但保持兼容 |
| major | `0.1.0 -> 1.0.0` | 重大变化或不兼容变化 |

如果当前版本已经是你要发布的版本，不要乱执行 `npm version patch`，否则会多升一级。

---

## 14. npm 2FA / Security Key 问题复盘

### 14.1 发布时报 403

常见报错：

```text
403 Forbidden
Two-factor authentication or granular access token with bypass 2fa enabled is required to publish packages.
```

含义：

```text
npm 账号开启了二次验证，发布包时必须完成 2FA。
```

解决：

```powershell
npm publish --access public --otp=你的npm验证码
```

### 14.2 `Enter OTP:` 要填什么

终端可能提示：

```text
This operation requires a one-time password.
Enter OTP:
```

这里的 OTP 可能是：

```text
1. 认证器 App 中的 6 位动态验证码；
2. 邮箱收到的一次性验证码；
3. Security Key / Passkey 认证流程生成的 token。
```

注意：

```text
npm 页面中显示的 Security Key 名称或编号不是 OTP。
```

例如：

```text
Security Key 171800
```

这只是安全密钥的名称或标识，不能直接填进终端。

### 14.3 邮箱收不到 OTP 怎么排查

如果 npm 页面提示已发送到邮箱，但邮箱没收到，可以检查：

```text
垃圾邮件
广告邮件
订阅邮件
拦截记录
邮箱规则
是否登录了正确 npm 账号
```

邮箱搜索关键词：

```text
npm
OTP
One-Time Password
OTP for logging in to your account
```

如果邮箱一直收不到，可以优先走 Security Key / WebAuthn / Passkey 流程。

### 14.4 为什么会弹出扫码

如果 Windows 安全中心或浏览器弹出二维码，通常是 WebAuthn / Passkey 的跨设备认证流程。

这不是普通二维码，也不是微信扫码。

它可能表示：

```text
浏览器认为你要使用手机作为安全密钥完成认证。
```

如果安全密钥绑定在手机上，就用手机扫码验证。

如果绑定在本机 Windows Hello 上，需要找：

```text
Windows Hello
此设备
本机安全密钥
Use security key
More choices
其他选项
```

不要把二维码或 Security Key 名称当成 OTP 填入终端。

---

## 15. 发布后检查

### 15.1 查看 npm 上的版本号

```powershell
npm view @czhanp/universal-watermark-skill version
```

含义：

```text
只查看 npm 上当前包的版本号。
```

期望输出类似：

```text
0.1.1
```

### 15.2 查看完整包信息

```powershell
npm view @czhanp/universal-watermark-skill
```

含义：

```text
查看 npm 上的包名、版本、描述、维护者、bin、发布时间等信息。
```

如果刚发布后立刻查询出现：

```text
404 Not Found
```

不一定是发布失败，可能是：

```text
1. npm registry 短暂同步延迟；
2. 本地 npm cache 尚未刷新；
3. registry 不是官方源；
4. 网络代理影响。
```

可以显式指定官方 registry 查询：

```powershell
npm view @czhanp/universal-watermark-skill --registry=https://registry.npmjs.org/
```

也可以先检查：

```powershell
npm config get registry
```

---

## 16. 用户安装和验证

### 16.1 推荐全局安装

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

含义：

```text
先把 npm 包全局安装到本机；
再把 Skill 安装到 Codex / Claude Code / agents 的技能目录。
```

### 16.2 检查安装目录

```powershell
dir $env:USERPROFILE\.codex\skills\universal-watermark
dir $env:USERPROFILE\.claude\skills\universal-watermark
dir $env:USERPROFILE\.agents\skills\universal-watermark
```

含义：

```text
检查 Skill 是否已经被复制到对应 agent 的 skills 目录。
```

### 16.3 验证 Python CLI

```powershell
python $env:USERPROFILE\.codex\skills\universal-watermark\scripts\universal_watermark.py --help
```

含义：

```text
确认安装后的 Python 水印脚本可以正常运行。
```

### 16.4 一次性安装，不保留全局 npm 包

```powershell
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

命令拆解：

| 部分 | 含义 |
|---|---|
| `npm exec` | 临时下载并执行 npm 包里的命令 |
| `--yes` | 自动确认安装提示 |
| `--package=...` | 指定要临时使用的 npm 包 |
| `--` | 后面的内容传给包内命令 |
| `universal-watermark-skill install --all` | 真正执行的安装器命令 |

这个写法比某些 `npx` 短写在 Windows 上更稳。

### 16.5 只下载一份本地目录

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill download universal-watermark
```

含义：

```text
把 Skill 文件复制到当前目录下的 universal-watermark 文件夹，不写入全局 agent 目录。
```

---

## 17. npx / bin 入口问题复盘

### 17.1 npx 的本质

`npx` 不是简单的“下载文件夹”工具。

它的核心作用是：

```text
临时下载 npm 包，并运行包里通过 package.json 的 bin 字段暴露出来的可执行命令。
```

所以，如果 `package.json` 没有配置好 `bin`，或者 `bin` 指向的文件没有被发布进 npm 包，`npx` 就不知道该运行什么。

### 17.2 曾经容易出错的写法

```powershell
npx @czhanp/universal-watermark-skill universal-watermark
```

或：

```powershell
npx --package=@czhanp/universal-watermark-skill universal-watermark-skill universal-watermark
```

在某些 Windows / npm / npx 组合中，可能报：

```text
'universal-watermark-skill' 不是内部或外部命令，也不是可运行的程序或批处理文件。
```

### 17.3 更稳的写法

推荐：

```powershell
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

或者全局安装后再运行：

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

### 17.4 本地测试 bin 入口

```powershell
npm link
```

含义：

```text
把当前本地包临时链接到全局环境，用来测试全局命令是否正常。
```

测试：

```powershell
universal-watermark-skill --help
```

取消链接：

```powershell
npm unlink -g @czhanp/universal-watermark-skill
```

---

## 18. 常用命令速查表

### 18.1 Git / GitHub 命令

| 命令 | 含义 | 常用场景 |
|---|---|---|
| `git status` | 查看当前 Git 状态 | 提交前必看 |
| `git init` | 初始化 Git 仓库 | 本地项目第一次使用 Git |
| `git branch -M main` | 把当前分支改名为 main | 和 GitHub 默认主分支统一 |
| `git remote -v` | 查看远程仓库地址 | 检查是否连到正确 GitHub 仓库 |
| `git remote add origin <url>` | 添加远程仓库 | 第一次绑定 GitHub |
| `git remote set-url origin <url>` | 修改远程仓库地址 | 仓库地址写错或迁移 |
| `git add .` | 添加当前目录新增/修改文件 | 普通提交 |
| `git add -A` | 添加所有变化，包括删除 | 有删除文件时更稳 |
| `git commit -m "说明"` | 创建一次提交 | 保存版本记录 |
| `git commit --amend --no-edit` | 修改上一次提交 | 刚提交后补小改动 |
| `git push -u origin main` | 第一次推送并设置 upstream | 首次上传 GitHub |
| `git push` | 普通推送 | 已设置 upstream 后 |
| `git pull --rebase origin main` | 拉取远程并把本地提交接上去 | 远程有本地没有的提交 |
| `git fetch origin main` | 获取远程最新状态但不合并 | 强推前更新远程引用 |
| `git push --force-with-lease` | 安全强制推送 | amend / rebase 后更新远程 |
| `git rm -r --cached <path>` | 从 Git 跟踪中移除文件但不删本地 | 清理误提交缓存 |

### 18.2 GitHub CLI 命令

| 命令 | 含义 | 常用场景 |
|---|---|---|
| `gh auth status` | 查看 GitHub CLI 登录状态 | 推送失败时检查 |
| `gh auth logout -h github.com` | 退出 GitHub CLI 登录 | token 失效时 |
| `gh auth login -h github.com -p https -w` | 浏览器登录 GitHub CLI | 重新授权 |
| `gh auth login -h github.com -p https -w --clipboard` | 登录并自动复制验证码 | 设备码登录时方便 |

### 18.3 PowerShell / 网络代理命令

| 命令 | 含义 | 常用场景 |
|---|---|---|
| `$env:HTTP_PROXY="http://127.0.0.1:7890"` | 设置 HTTP 临时代理 | 当前 PowerShell 让工具走 Clash |
| `$env:HTTPS_PROXY="http://127.0.0.1:7890"` | 设置 HTTPS 临时代理 | GitHub/npm 网络访问 |
| `$env:ALL_PROXY="socks5://127.0.0.1:7890"` | 设置通用代理 | 某些工具走 SOCKS |
| `Resolve-DnsName github.com` | 查看 github.com 解析结果 | 排查是否被 hosts 指到 127.0.0.1 |
| `Test-NetConnection github.com -Port 443` | 测试 GitHub HTTPS 连通性 | 排查网络连接 |
| `ipconfig /flushdns` | 刷新 DNS 缓存 | 改 hosts 后使用 |

### 18.4 npm 命令

| 命令 | 含义 | 常用场景 |
|---|---|---|
| `node --version` | 查看 Node.js 版本 | 发布前检查环境 |
| `npm --version` | 查看 npm 版本 | 发布前检查环境 |
| `npm install -g npm@latest` | 升级 npm | npm 太旧时 |
| `npm login --auth-type=web` | 浏览器登录 npm | 处理 2FA / Security Key |
| `npm logout` | 退出 npm 登录 | 登录状态混乱时 |
| `npm whoami` | 查看 npm 当前登录账号 | 发布前确认账号 |
| `npm config get registry` | 查看 registry | 查询/发布失败时检查源 |
| `npm config set registry https://registry.npmjs.org/` | 设置官方 registry | 避免镜像源影响发布 |
| `npm pack --dry-run` | 模拟打包 | 发布前检查文件清单 |
| `npm publish --access public` | 公开发布 scoped package | 正式发布 |
| `npm publish --access public --otp=xxxxxx` | 带 2FA 验证发布 | npm 要求 OTP 时 |
| `npm view <包名>` | 查看 npm 包信息 | 发布后检查 |
| `npm view <包名> version` | 只查看版本号 | 快速确认版本 |
| `npm version patch` | 升级 patch 版本 | 修 bug 后准备重新发布 |
| `npm install -g <包名>` | 全局安装 npm 包 | 用户安装 |
| `npm exec --yes --package=<包名> -- <命令>` | 临时执行 npm 包命令 | 一次性安装 Skill |
| `npm link` | 本地链接测试 npm bin | 发布前测试命令入口 |
| `npm unlink -g <包名>` | 取消本地全局链接 | 测试结束清理 |

---

## 19. 下次第一次上传新项目的行动清单

### 第一步：整理项目目录

确认有：

```text
README.md
SKILL.md
scripts/
LICENSE
.gitignore
package.json
```

确认不要有：

```text
__pycache__/
*.pyc
.venv/
.env
临时测试输出文件
```

### 第二步：进入目录

```powershell
cd "你的项目路径"
```

### 第三步：写好 .gitignore

```powershell
@"
__pycache__/
*.py[cod]
*$py.class

.venv/
venv/
.env

node_modules/
*.tgz
npm-debug.log*

.DS_Store
Thumbs.db
"@ | Set-Content -Encoding UTF8 .gitignore
```

### 第四步：Git 初始化并绑定远程

```powershell
git init
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

如果 `origin` 已存在：

```powershell
git remote set-url origin https://github.com/你的用户名/你的仓库名.git
```

### 第五步：提交并推送

```powershell
git status
git add -A
git commit -m "Initial release"
git push -u origin main
```

如果远程已有提交：

```powershell
git pull --rebase origin main
git push
```

如果确认远程可以被覆盖：

```powershell
git fetch origin main
git push -u origin main --force-with-lease
```

---

## 20. 下次更新项目并重新发布 npm 的行动清单

### 第一步：修改代码后提交 GitHub

```powershell
git status
git add -A
git commit -m "Update universal watermark skill"
git push
```

### 第二步：发布前检查

```powershell
npm whoami
npm config get registry
node -e "const p=require('./package.json'); console.log(p.name, p.version, p.bin)"
node bin/install.js --help
npm pack --dry-run
```

### 第三步：需要时升级版本号

如果当前版本已经发布过：

```powershell
npm version patch
```

然后推送版本号改动：

```powershell
git push
git push --tags
```

### 第四步：发布 npm

```powershell
npm publish --access public
```

如果要求 2FA：

```powershell
npm publish --access public --otp=你的npm验证码
```

### 第五步：发布后检查

```powershell
npm view @czhanp/universal-watermark-skill version
npm view @czhanp/universal-watermark-skill
```

### 第六步：安装验证

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
python $env:USERPROFILE\.codex\skills\universal-watermark\scripts\universal_watermark.py --help
```

或使用一次性安装：

```powershell
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

---

## 21. 最后记忆版：遇到问题先看这里

### 21.1 GitHub 推不上去

先看状态：

```powershell
git status
git remote -v
```

如果是登录问题：

```powershell
gh auth status
gh auth login -h github.com -p https -w
```

如果是代理问题：

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
$env:ALL_PROXY="socks5://127.0.0.1:7890"
```

如果是远程有本地没有的提交：

```powershell
git pull --rebase origin main
git push
```

如果确认可以覆盖远程：

```powershell
git fetch origin main
git push --force-with-lease
```

### 21.2 npm 发布失败

先检查：

```powershell
npm whoami
npm config get registry
npm pack --dry-run
```

如果是 2FA：

```powershell
npm publish --access public --otp=你的npm验证码
```

如果版本号重复：

```powershell
npm version patch
npm publish --access public
```

如果刚发布查不到：

```powershell
npm view @czhanp/universal-watermark-skill --registry=https://registry.npmjs.org/
```

### 21.3 用户安装失败

优先推荐：

```powershell
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all
```

如果不想全局安装：

```powershell
npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

检查目录：

```powershell
dir $env:USERPROFILE\.codex\skills\universal-watermark
```

验证 Python：

```powershell
python $env:USERPROFILE\.codex\skills\universal-watermark\scripts\universal_watermark.py --help
```

---

## 22. 学习这些命令的方式

不要死背命令，要按“动词 + 对象 + 参数”的方式理解。

### 22.1 Git 命令

```text
git status
git add
git commit
git push
git pull
git fetch
git remote
```

理解为：

```text
status  = 看状态
add     = 准备提交
commit  = 保存版本
push    = 推到远程
pull    = 从远程拉下来并合并/变基
fetch   = 只拿远程信息，不动当前文件
remote  = 管理远程仓库地址
```

### 22.2 npm 命令

```text
npm login
npm whoami
npm pack
npm publish
npm view
npm install
npm exec
npm version
```

理解为：

```text
login    = 登录
whoami   = 看当前是谁
pack     = 打包检查
publish  = 发布
view     = 查看线上包信息
install  = 安装
exec     = 临时执行包命令
version  = 改版本号
```

### 22.3 一句话记忆

```text
GitHub 上传看 git；
npm 发布看 package.json；
安装失败看 bin；
文件多了看 files / .npmignore；
推送失败看 remote / pull / force-with-lease；
验证码失败看 npm 2FA，不要拿 GitHub 验证码填 npm。
```
