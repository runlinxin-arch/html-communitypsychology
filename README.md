# 社区心理学阅读汇报 · 第六章《社区的文明观》

一份自包含的单文件网页幻灯片（讲者备注、翻页动效、打印版式齐备），外加一个 HeroUI 做的互动附录，以及配套讲稿与资料。

## 交付物（双击即可打开）

| 文件 | 说明 |
| --- | --- |
| `社区文明观-阅读汇报.html` | 主交付物。单文件、图片已内嵌；网页里按 `N` 调出讲者备注 |
| `社区文明观-阅读汇报.pdf` | 由主交付物导出的 14 页 PDF（960×540pt，对应 1280×720px） |
| `社区文明观-互动附录.html` | 互动附录的单文件成品，由 `npm run build` 构建后自动同步过来 |

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `build/deck-src-未内嵌图片.html` | **主幻灯片的源文件**，一切修改都从这里开始 |
| `build/重建.py` | 重建管线：内嵌图 → 重写根目录 HTML → 无头 Chrome 重导 PDF → 复核 |
| `build/检查.py` | 交付物一致性检查（见下） |
| `build/hooks/pre-commit` | 提交前自动跑上面的检查（只提醒，不阻断） |
| `互动附录-社区文明观/` | 互动附录工程（Vite + React 19 + HeroUI v3 + Tailwind 4） |
| `讲稿-社区文明观-阅读汇报.md` | 逐页讲稿，与幻灯片备注同源 |
| `资料包-第06章汇报.md`、`第六章社区的文明观.md`、`第06章-社区的文明观.md` | 章节原文与汇报资料 |
| `预览/` | 版式预览图、封面底图、图标线稿 |
| `notes/idea-briefs/` | 选题阶段的想法简报 |

## 换一台机器接着改

```bash
git clone https://github.com/runlinxin-arch/html-communitypsychology.git
cd html-communitypsychology
git config core.hooksPath build/hooks   # 启用提交前检查（本地配置，克隆后需重设一次）
```

**改主幻灯片。** 编辑 `build/deck-src-未内嵌图片.html`，然后：

```bash
python3 build/重建.py
```

脚本会重新内嵌图片、写出根目录的 HTML、用无头 Chrome 重导 PDF，并复核占位符残留、内嵌图数量、逐页溢出与 PDF 页数。

> 不要直接改成品 HTML──下次重建会覆盖它。另外 `build/重建.py` 顶部写死了 macOS 的 Chrome 路径
> （`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`），换到 Windows/Linux 需要先改这一行。

**改互动附录。**

```bash
cd 互动附录-社区文明观
npm install        # node_modules 不入库，克隆后必须装依赖
npm run dev        # 本地开发
npm run build      # 构建单文件，并自动同步成根目录的 社区文明观-互动附录.html
```

**交付物一致性检查。** 源改了但成品没重建、根目录副本过期、页码口径不同步，都会在这里被点出来：

```bash
python3 build/检查.py            # 只提醒，退出码 0
python3 build/检查.py --strict   # 有问题退出码 1
```

环境要求：Node ≥ 20（本机 v24.19.0）、npm 11、Python 3.9+；重建 PDF 需要本机装有 Google Chrome。
