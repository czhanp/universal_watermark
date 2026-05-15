#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const packageRoot = path.resolve(__dirname, "..");
const skillName = "universal-watermark";

const itemsToCopy = [
  "SKILL.md",
  "README.md",
  "README_zh-CN.md",
  "LICENSE",
  "scripts",
  "example",
  "examples"
];

const targetResolvers = {
  codex: (root) => path.join(root, ".codex", "skills", skillName),
  claude: (root) => path.join(root, ".claude", "skills", skillName),
  agents: (root) => path.join(root, ".agents", "skills", skillName)
};

function printUsage() {
  console.log(`
universal-watermark-skill

Install universal-watermark as a persistent Agent Skill, or download a local copy.

Usage:
  universal-watermark-skill install [--all] [--target codex|claude|agents] [--root <home-dir>]
  universal-watermark-skill download [output-dir]
  universal-watermark-skill --help

Examples:
  universal-watermark-skill install --all
  universal-watermark-skill install --target codex
  universal-watermark-skill download universal-watermark

Default install targets:
  Codex:       %USERPROFILE%\\.codex\\skills\\universal-watermark
  Claude Code: %USERPROFILE%\\.claude\\skills\\universal-watermark
  Agents:      %USERPROFILE%\\.agents\\skills\\universal-watermark
`);
}

function parseArgs(argv) {
  const args = [...argv];
  const command = args[0] && !args[0].startsWith("-") ? args.shift() : "install";
  const options = {
    command,
    all: false,
    targets: [],
    root: process.env.UNIVERSAL_WATERMARK_SKILL_HOME || os.homedir(),
    outputDir: null
  };

  if (command === "download") {
    options.outputDir = args[0] || skillName;
    return options;
  }

  while (args.length > 0) {
    const arg = args.shift();
    if (arg === "--help" || arg === "-h") {
      options.command = "help";
    } else if (arg === "--all") {
      options.all = true;
    } else if (arg === "--target") {
      const target = args.shift();
      if (!target) throw new Error("--target requires a value: codex, claude, or agents");
      options.targets.push(target);
    } else if (arg === "--root") {
      const root = args.shift();
      if (!root) throw new Error("--root requires a directory path");
      options.root = path.resolve(root);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (options.command === "install" && (options.all || options.targets.length === 0)) {
    options.targets = Object.keys(targetResolvers);
  }

  return options;
}

function shouldSkip(src) {
  const base = path.basename(src);
  return (
    base === "__pycache__" ||
    base === ".git" ||
    base === "node_modules" ||
    /\.pyc(\..*)?$/.test(base) ||
    base === ".env"
  );
}

function copyRecursive(src, dest) {
  if (!fs.existsSync(src) || shouldSkip(src)) return;

  const stat = fs.statSync(src);

  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });

    for (const item of fs.readdirSync(src)) {
      copyRecursive(path.join(src, item), path.join(dest, item));
    }

    return;
  }

  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function copySkillTo(targetDir, { allowExisting }) {
  if (fs.existsSync(targetDir) && fs.readdirSync(targetDir).length > 0 && !allowExisting) {
    throw new Error(`Target directory already exists and is not empty: ${targetDir}`);
  }

  fs.mkdirSync(targetDir, { recursive: true });

  for (const item of itemsToCopy) {
    copyRecursive(path.join(packageRoot, item), path.join(targetDir, item));
  }
}

function installSkill(options) {
  const installed = [];

  for (const target of options.targets) {
    const resolveTarget = targetResolvers[target];
    if (!resolveTarget) {
      throw new Error(`Unknown target "${target}". Expected one of: ${Object.keys(targetResolvers).join(", ")}`);
    }

    const targetDir = resolveTarget(options.root);
    copySkillTo(targetDir, { allowExisting: true });
    installed.push({ target, targetDir });
  }

  console.log("");
  console.log("universal-watermark skill installed successfully.");
  for (const item of installed) {
    console.log(`  ${item.target}: ${item.targetDir}`);
  }
  console.log("");
  console.log("Next steps:");
  console.log("  pip install pillow lxml python-docx pymupdf python-pptx");
  console.log("  Restart or reload your agent so it can discover the new skill.");
  console.log("");
}

function downloadSkill(options) {
  const targetDir = path.resolve(process.cwd(), options.outputDir);
  copySkillTo(targetDir, { allowExisting: false });

  console.log("");
  console.log("universal-watermark skill downloaded successfully.");
  console.log(`Output directory: ${targetDir}`);
  console.log("");
  console.log("Next steps:");
  console.log(`  cd "${targetDir}"`);
  console.log("  pip install pillow lxml python-docx pymupdf python-pptx");
  console.log("  python scripts/universal_watermark.py --help");
  console.log("");
}

function main() {
  try {
    const options = parseArgs(process.argv.slice(2));

    if (options.command === "help" || options.command === "--help" || options.command === "-h") {
      printUsage();
      return;
    }

    if (options.command === "install") {
      installSkill(options);
      return;
    }

    if (options.command === "download") {
      downloadSkill(options);
      return;
    }

    throw new Error(`Unknown command: ${options.command}`);
  } catch (error) {
    console.error("");
    console.error(error.message);
    printUsage();
    process.exit(1);
  }
}

main();
