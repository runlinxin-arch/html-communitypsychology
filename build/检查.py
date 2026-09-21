#!/usr/bin/env python3
"""交付物一致性检查：防止「源改了、成品没重建」这类静默过期。

用法（工作区根目录）：
    python3 build/检查.py            # 只提醒，退出码 0
    python3 build/检查.py --strict   # 有问题就退出码 1

检查五类：
  1) 时间戳链：源 → 成品 → PDF / dist → 根目录交付副本
  2) 内容指纹：根目录副本与 dist 的 sha256 是否一致（比时间戳硬）
  3) 结构完整性：占位符残留、内嵌图数量、页数/备注数
  4) 口径一致性：附录页码是否都在 deck 里、禁用词表是否还有残留
  5) 动效不变量：翻页动效必须每次重播、新页不能半透明、打印与减弱动效要有兜底
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DECK_SRC = ROOT / "build" / "deck-src-未内嵌图片.html"
DECK_HTML = ROOT / "社区文明观-阅读汇报.html"
DECK_PDF = ROOT / "社区文明观-阅读汇报.pdf"
FINGERPRINT = ROOT / "build" / "成品指纹.json"
APP = ROOT / "互动附录-社区文明观"
APP_DIST = APP / "dist" / "index.html"
APP_ROOT_COPY = ROOT / "社区文明观-互动附录.html"
SCRIPT = ROOT / "讲稿-社区文明观-阅读汇报.md"

# 编辑后立刻构建是常态，留一点容差，避免秒级顺序造成误报
TOLERANCE = 5.0

# 已经纠正过的旧口径：一旦再出现，说明某处没同步
BANNED = [
    ("样本只有一个小区", "样本口径 →「两个小区、一名汇报人」"),
    ("看不见未来", "三扇看不见 → 第三扇写作「看不见将来」"),
]

# 手工维护的副本（不是构建产物）：必须与原件逐字节相同，否则改一处、另一处静默过期。
# 被选中的判据：原件与副本内容一致、且副本是手写的（构建产物另有 1') 那段管）。
MIRRORS: list[tuple[pathlib.Path, pathlib.Path, str]] = [
    (SCRIPT, APP / "src" / "讲稿.md",
     "附录的「讲稿」抽屉读的是这份副本（src/script.ts 用 ?raw 导入）"),
]

# 动效这块踩过的坑都是「看着没事、实际有事」，写成静态断言钉住
ANIM_RULES = [
    # （正则, 期望命中?, 说明）
    (r"\.animate\(\[", True,
     "翻页动效必须用 Web Animations API 每次重播；退回「加类/去类」驱动的话，回看已访问过的页时类没变化，动画会静默丢失"),
    (r"\.slide\.ready\s+\.anim", False,
     "出现了旧的类驱动写法 .slide.ready .anim → 回看旧页会没有动效"),
    (r"\.slide\.on\{[^}]*transition", False,
     "新页 .slide.on 不能带 transition：新旧两页同时半透明时，中间会闪出深色底（实测亮度掉 30%）"),
    (r"\.slide\.out\{[^}]*transition:opacity", True,
     "淡出必须由「上一页压在新页上层淡出」实现（.slide.out），否则没有交叉溶解"),
    (r"--anim-wipe:", True, "缺少 --anim-wipe 变量：文字擦出的时长"),
]

# 这两条兜底一旦缺失，打印出来的 PDF 会大片缺字/空白
FALLBACK_RULES = [
    (r"@media print\{[\s\S]*?\.anim-text\{clip-path:none", "打印时没有 .anim-text{clip-path:none} → PDF 会缺字"),
    (r"prefers-reduced-motion: reduce\)\{[\s\S]*?\.anim-text\{clip-path:none", "减弱动效时没有强制终态 → 开了系统「减弱动态效果」的人会看不到内容"),
]

# 封面（P0）已经按用户要求去掉底图与信箱动画：静态断言钉死，防止手一滑又回来。
# 底图是 291 KB 的 JPEG，占成品近一半体积；信箱那套（.mails/.mbdoor/.mbhit + 六个函数）整块撤掉，
# 现在封面右侧只剩一个「一字未改」的 mailbox-01 线稿：viewBox 24×24、stroke-width 1.5。
COVER_ICON_VIEWBOX = (24.0, 24.0)
COVER_ICON_STROKE = 1.5
# 每条 = (标签, 匹配式, 说明)。匹配式同时认 CSS 选择器写法（.letter）和标签写法（class="letter"），
# 并且用 (?![-\w]) 挡住 letter-spacing 这类同前缀词——否则一条误报就能毁掉整个检查的可信度。
def _dead(cls: str) -> str:
    c = re.escape(cls)
    return rf"\.{c}(?![-\w])|class=\"[^\"]*(?<![-\w]){c}(?![-\w])"


DEAD_COVER_TOKENS = [
    ("cover-bg", _dead("cover-bg"), "封面的底图容器"),
    ("__COVER__", r"__COVER__", "封面底图占位符"),
    ("mailbox", _dead("mailbox"), "封面的信箱容器"),
    ("mails", _dead("mails"), "信封层"),
    ("letter", _dead("letter"), "信封"),
    ("mbdoor", _dead("mbdoor"), "信箱门扇"),
    ("mbsvg", _dead("mbsvg"), "信箱 SVG 容器"),
    ("mbhit", _dead("mbhit"), "信箱命中矩形"),
    ("mbpost", _dead("mbpost"), "信箱立柱"),
    ("mbcavity", _dead("mbcavity"), "信箱内腔"),
    ("mbhandle", _dead("mbhandle"), "信箱把手"),
    ("resetMailbox", r"\bresetMailbox\b", "信箱开合 JS"),
    ("openMailbox", r"\bopenMailbox\b", "信箱开合 JS"),
    ("closeMailbox", r"\bcloseMailbox\b", "信箱开合 JS"),
]

# 只该在封面出现的死代码：全篇任一页出现都算残留
DECK_WIDE_DEAD = {"mailbox", "mails", "letter", "mbdoor", "mbsvg", "mbhit", "mbpost",
                  "mbcavity", "mbhandle", "resetMailbox", "openMailbox", "closeMailbox"}


def strip_comments(src: str) -> str:
    """去掉 HTML 与 CSS 注释再扫「残留代码」——注释里提到类名不算残留。"""
    src = re.sub(r"<!--[\s\S]*?-->", "", src)
    return re.sub(r"/\*[\s\S]*?\*/", "", src)


def cover_section(src: str):
    """取出 P0 封面那一段 HTML。"""
    m = re.search(r'<section class="slide dark on">([\s\S]*?)</section>', src)
    return m.group(1) if m else None


problems: list[str] = []
notes: list[str] = []


def mtime(p: pathlib.Path) -> float | None:
    return p.stat().st_mtime if p.exists() else None


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def newest(paths) -> tuple[float, pathlib.Path] | None:
    hit = [(mtime(p), p) for p in paths if p.is_file() and mtime(p) is not None]
    return max(hit) if hit else None


def check(files: list[pathlib.Path]) -> None:
    for p in files:
        if not p.exists():
            problems.append(f"文件缺失：{p.relative_to(ROOT)}")


def main() -> int:
    check([DECK_SRC, DECK_HTML, DECK_PDF, APP_DIST, APP_ROOT_COPY, SCRIPT,
           *[c for _, c, _ in MIRRORS]])

    # 1) 时间戳链：deck 源 → 成品 → PDF
    if DECK_SRC.exists() and DECK_HTML.exists():
        if mtime(DECK_SRC) > mtime(DECK_HTML) + TOLERANCE:
            problems.append("deck 源文件比成品 HTML 新 → 跑 python3 build/重建.py")
    # 成品 HTML ↔ PDF 用内容指纹比对，不用时间戳（git checkout 复原文件不会误报）
    if FINGERPRINT.exists():
        fp = json.loads(FINGERPRINT.read_text(encoding="utf-8"))
        if DECK_HTML.exists() and sha(DECK_HTML) != fp.get("html_sha256"):
            problems.append("deck 成品 HTML 与上次导出 PDF 时不是同一版本 → 跑 python3 build/重建.py")
        if DECK_PDF.exists() and sha(DECK_PDF) != fp.get("pdf_sha256"):
            problems.append("deck PDF 与记录不符（被替换或未重导）→ 跑 python3 build/重建.py")
        notes.append(f"指纹：上次导出 PDF 于 {fp.get('exported_at', '?')}")
    else:
        problems.append("缺少 build/成品指纹.json → 跑 python3 build/重建.py 生成")

    # 1') 时间戳链：附录 源 → dist，dist → 根目录副本
    if APP_DIST.exists():
        src_latest = newest([*APP.glob("src/**/*"), APP / "package.json",
                             APP / "vite.config.ts", APP / "index.html"])
        if src_latest and src_latest[0] > mtime(APP_DIST) + TOLERANCE:
            rel = src_latest[1].relative_to(ROOT)
            problems.append(f"附录源文件比构建产物新（{rel}）→ 跑 cd 互动附录-社区文明观 && npm run build")
        if APP_ROOT_COPY.exists() and sha(APP_DIST) != sha(APP_ROOT_COPY):
            problems.append("根目录交付副本与 dist 内容不一致 → 跑 node 互动附录-社区文明观/scripts/同步交付物.mjs")

    # 2') 手工维护的副本：用 sha256 比对，不看时间戳
    for orig, copy, why in MIRRORS:
        if not (orig.exists() and copy.exists()):
            continue
        if sha(orig) != sha(copy):
            problems.append(f"副本与原件不一致：{copy.relative_to(ROOT)} 与 {orig.relative_to(ROOT)} 内容不同"
                            f"（{why}）→ 跑 cp \"{orig.name}\" \"{copy.relative_to(ROOT)}\" 同步后再 npm run build")
        else:
            notes.append(f"副本：{copy.relative_to(ROOT)} 与 {orig.name} 逐字节一致")

    # 3) 结构完整性
    if DECK_HTML.exists():
        html = DECK_HTML.read_text(encoding="utf-8")
        for token in ("__COVER__", "__CANA__"):
            if token in html:
                problems.append(f"deck 成品里残留占位符 {token}")
        n_img = html.count("data:image")
        # 期望张数 = 源文件里还剩几个图片占位符（现在只剩 __CANA__ 一张）
        want_img = sum(1 for t in ("__COVER__", "__CANA__") if t in DECK_SRC.read_text(encoding="utf-8")) \
            if DECK_SRC.exists() else 1
        if n_img != want_img:
            problems.append(f"deck 成品内嵌图 {n_img} 张（源里尚有 {want_img} 个占位符）→ 成品与源不同步")
        n_slide = len(re.findall(r'<section class="slide', html))
        n_notes = len(re.findall(r'<aside class="notes"', html))
        if n_slide != 14:
            problems.append(f"deck 幻灯片 {n_slide} 页（应为 14）")
        if n_notes != 10:
            problems.append(f"deck 备注 {n_notes} 条（应为 10）")
        notes.append(f"deck：{n_slide} 页 / {n_notes} 条备注 / {n_img} 张内嵌图")
    if DECK_PDF.exists():
        try:
            info = subprocess.run(["pdfinfo", str(DECK_PDF)], capture_output=True, text=True).stdout
            pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
            size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+)", info, re.M)
            if pages and pages.group(1) != "14":
                problems.append(f"deck PDF {pages.group(1)} 页（应为 14）")
            if size and (round(float(size.group(1))) != 960 or round(float(size.group(2))) != 540):
                problems.append(f"deck PDF 页面尺寸 {size.group(1)}×{size.group(2)}pt（应为 960×540）")
            if pages:
                notes.append(f"PDF：{pages.group(1)} 页 {size.group(1)}×{size.group(2)}pt"
                             if size else f"PDF：{pages.group(1)} 页")
        except FileNotFoundError:
            notes.append("PDF：跳过（没有 pdfinfo）")

    # 4) 口径一致性
    if DECK_SRC.exists():
        src = DECK_SRC.read_text(encoding="utf-8")
        for pat, want, why in ANIM_RULES:
            hit = re.search(pat, src) is not None
            if hit != want:
                problems.append(f"deck 动效：{why}")
        for pat, why in FALLBACK_RULES:
            if re.search(pat, src) is None:
                problems.append(f"deck 动效兜底：{why}")
        # 封面：无底图、无信箱动画，只剩一个未改动的 mailbox-01 线稿
        bare = strip_comments(src)
        cover = cover_section(bare)
        if cover is None:
            problems.append("deck 封面：解析不到 P0 封面段落（<section class=\"slide dark on\"> 变了？）")
        else:
            for label, pat, why in DEAD_COVER_TOKENS:
                if re.search(pat, cover):
                    problems.append(f"deck 封面：{why}又出现了（{label}）→ 用户已要求撤掉")
            if "data:image" in cover:
                problems.append("deck 封面：又内嵌了图片 → 用户已要求删除首页背景图")
            icon = re.search(r'<div class="cover-mark"[^>]*>\s*<svg viewBox="0 0 ([\d.]+) ([\d.]+)"', cover)
            if icon is None:
                problems.append("deck 封面：找不到 .cover-mark 里的 mailbox-01 线稿")
            else:
                vw, vh = float(icon.group(1)), float(icon.group(2))
                if (vw, vh) != COVER_ICON_VIEWBOX:
                    problems.append(f"deck 封面：线稿 viewBox 是 {vw:g}×{vh:g}，应为 24×24（图标被改过比例）")
                stroke = re.search(r"\.cover-mark svg\{[^}]*?stroke-width:([\d.]+)", bare)
                if stroke is None or abs(float(stroke.group(1)) - COVER_ICON_STROKE) > 0.001:
                    problems.append("deck 封面：线稿 stroke-width 不是原始的 1.5（描边被改过）")
                if re.search(r'class="cover-mark"[^>]*(tabindex|role)=', cover):
                    problems.append("deck 封面：线稿被做成了可交互元素（tabindex/role）→ 应保持纯装饰")
            notes.append("封面：无底图、无信箱动画，只剩静态 mailbox-01 线稿（viewBox 24×24 / 描边 1.5）")
        # 全篇不该再残留任何信箱动效代码（已去掉注释，注释里提类名不算）
        for label, pat, why in DEAD_COVER_TOKENS:
            if label in DECK_WIDE_DEAD and re.search(pat, bare):
                problems.append(f"deck：还残留{why}的代码（{label}）→ 应已整块撤掉")

        if not problems:
            notes.append(f"动效：{len(ANIM_RULES) + len(FALLBACK_RULES)} 条不变量通过")

    appendix_refs: set[str] = set()
    for f in APP.glob("src/**/*.ts*"):
        appendix_refs |= set(re.findall(r"p\.\s?\d+(?:\s?[–-]\s?\d+)?", f.read_text(encoding="utf-8")))
    if appendix_refs and DECK_HTML.exists():
        deck_refs = set(re.findall(r"p\.\s?\d+(?:\s?[–-]\s?\d+)?", DECK_HTML.read_text(encoding="utf-8")))
        orphan = {r.replace(" ", "") for r in appendix_refs} - {r.replace(" ", "") for r in deck_refs}
        if orphan:
            problems.append(f"附录引了 deck 没有的页码：{sorted(orphan)}")
        notes.append(f"页码：附录 {len(appendix_refs)} 个引用，全部能在 deck 找到"
                     if not orphan else "页码：存在孤儿引用")

    targets = {"deck 成品": DECK_HTML, "讲稿": SCRIPT, "附录": APP.joinpath("src", "data.ts")}
    for words, why in BANNED:
        for name, p in targets.items():
            if p.exists() and words in p.read_text(encoding="utf-8"):
                problems.append(f"{name} 里还有旧口径「{words}」（{why}）")

    # 输出
    print("交付物一致性检查")
    for n in notes:
        print(f"  · {n}")
    if problems:
        print(f"\n发现 {len(problems)} 个问题：")
        for p in problems:
            print(f"  ⚠ {p}")
        return 0 if "--strict" not in sys.argv else 1
    print("\n  ✅ 全部一致（源→成品→PDF、附录→dist→根目录副本、页码与口径）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
