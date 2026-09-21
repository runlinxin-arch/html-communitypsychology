#!/usr/bin/env node
/**
 * 把构建产物同步成工作区根目录下的交付副本。
 *
 * 为什么要这一步：dist/index.html 是单文件成品，但它在工程目录里，不便于双击交付；
 * 而手抄一份到根目录必然会过期——所以把复制钉在 npm run build 上，构建即同步。
 *
 * 用法：npm run build（自动调用）或 node scripts/同步交付物.mjs（只同步不构建）
 */
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const project = resolve(here, "..");
const built = resolve(project, "dist/index.html");
const targetDir = resolve(project, "..");
const target = resolve(targetDir, "社区文明观-互动附录.html");

const sha = (p) => createHash("sha256").update(readFileSync(p)).digest("hex").slice(0, 12);
const size = (p) => (readFileSync(p).length / 1024 / 1024).toFixed(2) + " MB";

if (!existsSync(built)) {
  console.error(`✗ 构建产物不存在：${built}`);
  console.error("  先跑 npm run build（或 npx vite build）再同步。");
  process.exit(1);
}

if (!existsSync(targetDir)) {
  console.log(`· 上级目录不存在（${targetDir}），跳过交付副本同步（独立构建时不视为错误）`);
  process.exit(0);
}

mkdirSync(targetDir, { recursive: true });
copyFileSync(built, target);

const [a, b] = [sha(built), sha(target)];
if (a !== b) {
  console.error(`✗ 复制后校验不一致：dist ${a} ≠ 根目录 ${b}`);
  process.exit(1);
}

console.log(`✓ 交付副本已同步：社区文明观-互动附录.html（${size(target)}，sha256 ${b}）`);
