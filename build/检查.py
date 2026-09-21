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
import math
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

# 每条 = (标签, 匹配式, 说明)。匹配式同时认 CSS 选择器写法（.letter）和标签写法（class="letter"），
# 并且用 (?![-\w]) 挡住 letter-spacing 这类同前缀词——否则一条误报就能毁掉整个检查的可信度。
def _dead(cls: str) -> str:
    c = re.escape(cls)
    return rf"\.{c}(?![-\w])|class=\"[^\"]*(?<![-\w]){c}(?![-\w])"


DEAD_COVER_TOKENS = [
    ("cover-bg", _dead("cover-bg"), "封面的底图容器"),
    ("__COVER__", r"__COVER__", "封面底图占位符"),
    ("mailbox", _dead("mailbox"), "旧的信箱容器"),
    ("mbsvg", _dead("mbsvg"), "旧信箱的 SVG 容器"),
    ("mbhit", _dead("mbhit"), "旧信箱的命中矩形"),
    ("mbdoor", _dead("mbdoor"), "旧信箱的门扇"),
    ("mbcase", _dead("mbcase"), "旧信箱的外壳"),
    ("mbpost", _dead("mbpost"), "旧信箱的立柱"),
    ("mbcavity", _dead("mbcavity"), "旧信箱的内腔"),
    ("mbhandle", _dead("mbhandle"), "旧信箱的把手"),
    ("mbfill", _dead("mbfill"), "旧信箱的门板"),
    ("mbline", _dead("mbline"), "旧信箱的门扇描边"),
    ("cover-mark", _dead("cover-mark"), "旧的 mailbox-01 线稿容器"),
    ("cap", _dead("cap"), "封面上的文字提示"),
    ("--d", r"--d:[-\d.]+m?s", "信纸延迟的旧 CSS 变量（延迟已改由 JS 的 STAGGER 控制，CSS 里这份是死代码）"),
    ("resetMailbox", r"\bresetMailbox\b", "旧信箱开合 JS"),
    ("openMailbox", r"\bopenMailbox\b", "旧信箱开合 JS"),
    ("closeMailbox", r"\bcloseMailbox\b", "旧信箱开合 JS"),
]

# 「已经撤掉的东西」全篇任一页出现都算残留
DECK_WIDE_DEAD = {label for label, _, _ in DEAD_COVER_TOKENS}

# 封面信封：信纸落点必须留在「无字安全带」里（用户要求「信不盖住文字」，靠留白带保证）。
# 带子来自封面各文字块实测包围盒：上边 = kicker 底 93，下边 = 标题块顶 371，
# 左边 = 版心 72，右边 = 信封左沿 950 再退 30（退多少就是信封与落点之间的净空）。
MAIL_SAFE = {"top": 100, "bottom": 360, "left": 80, "right": 920}
MAIL_PAD = 14        # 漂浮振幅（|dx|≤9、|dy|≤11）＋漂浮时再转 1.6° 的包围盒增量
LETTER_COUNT = 5     # 用户要求「大约 4、5 封」
FLY_MS = 2500        # 用户指定：每封信飘出 2.5 秒
MIN_DY_SPREAD = 80   # 5 封信的纵向跨度下限，低于这个数就不叫「高低错落」
ENV_TOP_MIN = 190    # 信封顶边下移后的下限（用户要求「整体下移一点」）
LEFT_BEIGE = "#EDE0C1"   # 信封的米色


def mail_geometry(src: str):
    """从 CSS 里解析信纸落点，算出每封信在屏幕坐标下的静态包围盒。"""
    m = re.search(r"\.envelope\{[^}]*?right:(\d+)px;top:(\d+)px;width:(\d+)px", src)
    mm = re.search(r"\.mails\{[^}]*?right:(\d+)px;top:(\d+)px;width:(\d+)px", src)
    l = re.search(r"\.letter\{[^}]*?top:(-?\d+)px;width:(\d+)px;height:(\d+)px", src)
    ml = re.search(r"\.letter\{[^}]*?margin-left:(-?\d+)px", src)
    if not (m and mm and l and ml):
        return None
    if m.groups() != mm.groups():
        return None            # 信封层与信纸层锚点不一致 → left:50% 不再是开口正中，落点公式失效
    right, mtop, mw = (int(v) for v in m.groups())
    ltop, lw, lh = (int(v) for v in l.groups())
    if int(ml.group(1)) != -lw // 2:
        return None            # 信纸没有在开口上水平居中，落点就不成立
    base_x, base_y = 1280 - right - mw / 2, mtop + ltop + lh / 2
    out = []
    for g in re.finditer(r'\.letter\[data-i="(\d+)"\]\{--tx:(-?\d+)px;--ty:(-?\d+)px;--rot:(-?[\d.]+)deg', src):
        i, tx, ty, rot = g.group(1), int(g.group(2)), int(g.group(3)), float(g.group(4))
        rad = math.radians(abs(rot))
        hw = (lw * math.cos(rad) + lh * math.sin(rad)) / 2
        hh = (lw * math.sin(rad) + lh * math.cos(rad)) / 2
        cx, cy = base_x + tx, base_y + ty
        out.append((i, cx - hw, cy - hh, cx + hw, cy + hh))
    return out


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
        # 封面：无底图、无 SVG，只有一个纯 CSS 信封 + 5 封信
        bare = strip_comments(src)
        cover = cover_section(bare)
        if cover is None:
            problems.append("deck 封面：解析不到 P0 封面段落（<section class=\"slide dark on\"> 变了？）")
        else:
            for label, pat, why in DEAD_COVER_TOKENS:
                if re.search(pat, cover):
                    problems.append(f"deck 封面：{why}又出现了（{label}）→ 用户已要求撤掉")
            if "<svg" in cover:
                problems.append("deck 封面：又出现了 SVG → 用户要求删掉 SVG 图片，信封要纯 CSS 画")
            if "data:image" in cover:
                problems.append("deck 封面：又内嵌了图片 → 用户已要求删除首页背景图")
            for cls, why in (("env-sway", "摇晃层"), ("env-shake", "震动层"), ("env-body", "外框"),
                             ("env-inner", "内衬"), ("env-flap", "上盖")):
                if f'class="{cls}"' not in cover:
                    problems.append(f"deck 封面：信封缺了{why}（.{cls}）")
            n_letters = len(re.findall(r'<div class="letter" data-i="', cover))
            if n_letters != LETTER_COUNT:
                problems.append(f"deck 封面：信纸 {n_letters} 封（应为 {LETTER_COUNT}）")
            if re.search(r'class="envelope"[^>]*role="button"[^>]*tabindex="0"', cover) is None:
                problems.append("deck 封面：信封不是可聚焦按钮（缺 role=button / tabindex=0）")
            if "点一下" in cover:
                problems.append("deck 封面：又出现了文字提示（「点一下…」）→ 已改成信封自己摇晃")
            notes.append(f"封面：无底图、无 SVG，纯 CSS 信封 + {n_letters} 封信")
        # 几何：5 封信的落点必须全在无字安全带里
        # 先查「信封有没有下移」：它必须独立于几何解析 —— 一改 top，两个锚点就不同步，
        # mail_geometry 直接返回 None，写在 else 里的断言反而永远走不到。
        env_top_m = re.search(r"\.envelope\{[^}]*?top:(-?\d+)px", src)
        if env_top_m is None:
            problems.append("deck 封面信封：读不出 .envelope 的 top → 下移与否没法核")
        else:
            env_top = int(env_top_m.group(1))
            if env_top < ENV_TOP_MIN:
                problems.append(f"deck 封面信封：信封顶边在 y={env_top}（应 ≥ {ENV_TOP_MIN}）→ 没有下移")
        geo = mail_geometry(src)
        if geo is None:
            problems.append("deck 封面信封：解析不到 .envelope/.mails/.letter 的几何参数"
                            "（锚点对不上、或 left:50% / margin-left 的居中写法变了）")
        else:
            if len(geo) != LETTER_COUNT:
                problems.append(f"deck 封面信封：只解析到 {len(geo)} 封信的落点（应为 {LETTER_COUNT}）")
            for i, l, t, r, b in geo:
                if (t - MAIL_PAD < MAIL_SAFE["top"] or b + MAIL_PAD > MAIL_SAFE["bottom"]
                        or l - MAIL_PAD < MAIL_SAFE["left"] or r + MAIL_PAD > MAIL_SAFE["right"]):
                    problems.append(
                        f"deck 封面信封：第 {i} 封信落点 x {l:.0f}–{r:.0f} / y {t:.0f}–{b:.0f}"
                        f"（含 {MAIL_PAD}px 余量）超出无字安全带 "
                        f"y {MAIL_SAFE['top']}–{MAIL_SAFE['bottom']}、x {MAIL_SAFE['left']}–{MAIL_SAFE['right']}"
                        f" → 会盖住封面的字或蹭到信封")
            tops = sorted(t for _, _, t, _, _ in geo)
            spread = tops[-1] - tops[0]
            if spread < MIN_DY_SPREAD:
                problems.append(f"deck 封面信封：5 封信的纵向跨度只有 {spread:.0f}px"
                                f"（应 ≥ {MIN_DY_SPREAD}px）→ 没有高低错落")
            notes.append(f"信封：{len(geo)} 封信落点都在无字安全带内"
                         f"（y {MAIL_SAFE['top']}–{MAIL_SAFE['bottom']}），纵向错落 {spread:.0f}px")
            if re.search(r"@media print\{[\s\S]*?\.mails \.letter\{opacity:1", src) is None:
                problems.append("deck 封面信封：打印规则里没有 .mails .letter{opacity:1} → 导出的 PDF 封面会少掉信")
        # 飘出时长 = 用户点名的 2.5 秒
        fly = re.search(r"var FLY=(\d+);", src)
        if fly is None or int(fly.group(1)) != FLY_MS:
            problems.append(f"deck 封面信封：飘出时长 FLY={fly.group(1) if fly else '缺'}ms，"
                            f"应为 {FLY_MS}ms（用户指定 2.5 秒）")
        # 上盖必须绕信封顶边掀开：transform-origin:50% 0，终态是 rotateX
        if re.search(r"\.env-flap\{[^}]*transform-origin:50% 0", src) is None:
            problems.append("deck 封面信封：上盖的 transform-origin 不是 50% 0 → 不是绕信封顶边掀开")
        if re.search(r"\.envelope\.lid \.env-flap\{transform:rotateX\(", src) is None:
            problems.append("deck 封面信封：缺少 .envelope.lid .env-flap 的 rotateX 终态")
        if re.search(r"\.envelope\.lid \.env-flap::before[^{]*\{opacity:", src) is None:
            problems.append("deck 封面信封：上盖掀开后没有压暗 → 翻折方向读不出来")
        # 米色：外框、上盖、内衬三条线必须走同一个变量
        if f"--beige:{LEFT_BEIGE}" not in src:
            problems.append(f"deck 封面信封：--beige 不是 {LEFT_BEIGE}（用户要求信封改成米色）")
        if re.search(r"\.env-body\{[^}]*border:1\.5px solid var\(--beige\)", src) is None:
            problems.append("deck 封面信封：外框描边没有用 --beige")
        if re.search(r"\.env-flap::before,\.env-flap::after,\.env-inner::before,\.env-inner::after\{[^}]*background:var\(--beige\)", src) is None:
            problems.append("deck 封面信封：上盖/内衬的线没有用 --beige")
        # 内衬：合上时隐在外盖底下，掀开后留在信封里 —— 不然打开的信封里是一块空白
        if re.search(r"\.env-flap,\.env-inner\{", src) is None:
            problems.append("deck 封面信封：内衬没有和上盖共用同一套坐标 → 两条 V 不会重合")
        dim = re.search(r"\.env-inner::before,\.env-inner::after\{opacity:([\d.]+)", src)
        if dim is None:
            problems.append("deck 封面信封：内衬没有做压暗 → 合上时会透出来")
        elif float(dim.group(1)) >= 0.6:
            problems.append(f"deck 封面信封：内衬的 opacity={dim.group(1)}（应 < 0.6）"
                            f" → 合上时会从外盖下面透出来")
        inn = re.search(r'class="env-inner"', cover)
        fl = re.search(r'class="env-flap"', cover)
        if inn and fl and inn.start() > fl.start():
            problems.append("deck 封面信封：内衬排在上盖之后 → 会盖住上盖，合上时看不见外盖")
        # 摇晃 + 震动：只在「点过之前」跑，两层分开才不会互相覆盖 transform
        for pat, why in ((r"@keyframes env-sway\{", "摇晃关键帧 env-sway"),
                         (r"@keyframes env-buzz\{", "震动关键帧 env-buzz"),
                         (r"\.envelope:not\(\.used\) \.env-sway\{animation:env-sway", "摇晃层的摇晃"),
                         (r"\.envelope:not\(\.used\) \.env-shake\{animation:env-buzz", "内层的震动")):
            if re.search(pat, src) is None:
                problems.append(f"deck 封面信封：缺少{why} → 没点过之前不会晃")
        # 摇晃不能挂回 .envelope：入场淡入是挂在它身上的 WAAPI 动画，写死了 transform，
        # WAAPI 压过 CSS animation → 摇晃会变成「有动画名但没有位移」的假动作
        if re.search(r"\.envelope:not\(\.used\)\{animation:env-sway", src):
            problems.append("deck 封面信封：摇晃挂回了 .envelope 本体 → 被入场 WAAPI 动画压掉，动不起来（应挂 .env-sway）")
        if "classList.remove('used')" in src:
            problems.append("deck 封面信封：used 类被移除了 → 合上之后又会开始摇晃（用户要求保持静止）")
        if re.search(r"box\.classList\.add\('used'\)", src) is None:
            problems.append("deck 封面信封：第一次点击没有给信封打上 used（停止摇晃的开关）")
        for pat, why in ((r"body\.noanim \.env-sway,body\.noanim \.env-shake\{animation:none",
                          "按 A 关动效时停掉摇晃"),
                         (r"prefers-reduced-motion: reduce\)\{[\s\S]{0,400}?\.env-sway,\.env-shake\{animation:none",
                          "系统「减弱动态效果」时停掉摇晃"),
                         (r"@media print\{[\s\S]*?\.env-sway,\.env-shake\{animation:none",
                          "打印时停掉摇晃")):
            if re.search(pat, src) is None:
                problems.append(f"deck 封面信封：缺少{why}的兜底")
        # 时序：先完全掀盖 → 再放信；先全部收信 → 再合盖
        door = re.search(r"var DOOR_MS=(\d+);", src)
        if door is None or int(door.group(1)) < 600:
            problems.append(f"deck 封面信封：DOOR_MS={door.group(1) if door else '缺'}ms"
                            f"（应 ≥ 600ms，也就是 CSS 里那 .6s 的掀盖过渡）")
        if re.search(r"launchLetters\(slide\);\},DOOR_MS\)", src) is None:
            problems.append("deck 封面信封：信没有等上盖完全掀开才飞（用户要求先展开、再逐一飞出）")
        # 合盖那一块要整个看：必须排在最后一封信收完之后，先摘类再撤动画，顺序不能反
        shut = re.search(r"later\(box,function\(\)\{([\s\S]{0,400}?)\}\,last\+40\);", src)
        if shut is None:
            problems.append("deck 封面信封：合盖没有排在最后一封信收完之后（应 last+40ms）")
        else:
            body = shut.group(1)
            if "remove('closing','open','lid')" not in body:
                problems.append("deck 封面信封：上盖没有等信全部收回才合上（用户要求先收信、再关信封）")
            elif "cancel()" not in body or body.index("cancel()") < body.index("remove("):
                problems.append("deck 封面信封：收信的动画没有在 .open 摘掉之后才撤 → 会掉回静态规则、信当场复现")
        # 掀盖那 .64s 里第二次点击必须能被接住：只认 .open 的话，这 640ms 内的点击会被吞掉
        if re.search(r"if\(box\.classList\.contains\('open'\)\|\|box\.classList\.contains\('opening'\)\)\{closeEnvelope", src) is None:
            problems.append("deck 封面信封：掀盖途中的第二次点击会被吞掉（只认 .open）→ 反悔不了")
        if re.search(r"if\(!box\|\|box\.classList\.contains\('closing'\)\)return;", src) is None:
            problems.append("deck 封面信封：closeEnvelope 的守卫拦掉了掀盖中的取消（应只拦 .closing）")
        if re.search(r"var from=getComputedStyle\(el\)\.transform;", src) is None:
            problems.append("deck 封面信封：收信没有从「当前所在位置」接上 → 半途点击会跳回去")
        # 全篇不该再残留任何旧信箱/旧线稿的代码（已去掉注释，注释里提类名不算）
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
