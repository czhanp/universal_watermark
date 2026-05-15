# npm 发布操作记录

## 项目

- 项目目录：`C:\Users\walke\Desktop\ALL\universal-watermark`
- GitHub 仓库：`https://github.com/czhanp/universal_watermark.git`
- npm 包定位：通过 `npx` 分发 Skill 文件，不提供 Node.js API
- 当前 npm 包名：`@czhanp/universal-watermark-skill`
- 当前版本：`0.1.1`

## 已完成的本地改动

1. 新增 `package.json`
   - 配置 `name`、`version`、`description`、`keywords`、`repository`、`license`
   - 配置 bin 命令：`universal-watermark-skill -> bin/install.js`
   - 配置 npm 发布文件清单
   - 显式排除 `scripts/**/__pycache__/**`、`*.pyc`、`*.pyc.*`

2. 新增 `bin/install.js`
   - 支持命令：

   ```bash
   npm install -g @czhanp/universal-watermark-skill
   universal-watermark-skill install --all
   ```

   - 复制内容：
     - `SKILL.md`
     - `README.md`
     - `README_zh-CN.md`
     - `LICENSE`
     - `scripts/`
     - `example/`
     - `examples/`，如果存在
   - 跳过 `__pycache__` 和 `.pyc` 文件
   - `install` 默认安装到 `.codex`、`.claude`、`.agents` 三个全局 skills 目录
   - `download` 保留旧版下载到本地目录的能力
   - 目标下载目录已存在且非空时会中止，避免覆盖用户文件

3. 更新 `.gitignore`
   - 增加：

   ```gitignore
   node_modules/
   *.tgz
   npm-debug.log*
   ```

4. 新增 `.npmignore`
   - 排除 Python 缓存、npm 缓存包、虚拟环境、`.env`、`.git`

5. 更新 `README.md`
   - 增加 `Download via npm` 小节
   - 说明 `npx` 下载方式和 Python 依赖安装方式

6. 更新 `README_zh-CN.md`
   - 增加“通过 npm 下载 Skill”小节
   - 说明 `npx` 下载方式和 Python 依赖安装方式

## 已执行的本地校验

1. 检查 Node / npm 版本

```bash
node --version
npm --version
```

结果：

```text
node v24.14.1
npm 11.11.0
```

2. 校验 `package.json` 可读取

```bash
node -e "const p=require('./package.json'); console.log(p.name, p.version, p.bin['universal-watermark-skill'])"
```

结果：

```text
@czhanp/universal-watermark-skill 0.1.1 bin/install.js
```

3. 测试安装脚本

```bash
node bin/install.js npm-install-test
```

结果：成功生成 Skill 目录，包含 `SKILL.md`、`README.md`、`README_zh-CN.md`、`LICENSE`、`scripts/`、`example/`。

4. 测试安装后的 Python CLI

```bash
python npm-install-test/scripts/universal_watermark.py --help
```

结果：成功显示 CLI 帮助，默认水印文字为 `内部资料`。

5. 检查 npm 打包内容

```bash
npm pack --dry-run
```

结果：成功。打包清单包含 23 个文件，未包含 `__pycache__` 和 `.pyc`。

关键输出：

```text
package: @czhanp/universal-watermark-skill@0.1.1
filename: czhanp-universal-watermark-skill-0.1.1.tgz
package size: 1.2 MB
total files: 23
```

## 当前阻塞点

当前机器尚未登录 npm：

```bash
npm whoami
```

结果：

```text
ENEEDAUTH
This command requires you to be logged in.
```

因此暂时不能执行真正的发布命令。

## 后续发布步骤

1. 登录 npm

```bash
npm login
```

登录后确认：

```bash
npm whoami
```

2. 确认 npm scope

当前包名为：

```text
@czhanp/universal-watermark-skill
```

如果你的 npm 用户名或组织名不是 `czhanp`，需要先修改 `package.json` 的 `name` 字段。

3. 发布 scoped public 包

```bash
npm publish --access public
```

4. 发布后测试

在空目录执行：

```bash
npm install -g @czhanp/universal-watermark-skill
universal-watermark-skill install --all

或者不保留全局 npm 包，只执行一次安装：

npm exec --yes --package=@czhanp/universal-watermark-skill -- universal-watermark-skill install --all
```

## 版本更新规则

npm 不允许重复发布相同的 `name + version`。后续再次发布前需要升级版本：

```bash
npm version patch
npm publish --access public
```
