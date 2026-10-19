#!/usr/bin/env python3
"""静态检查《精神健康系统》阅读汇报单文件成品。

用法：
    python3 构建/检查.py            # 开发中；不因“待填”失败
    python3 构建/检查.py --strict   # 交付前；任何页码/占位残留都失败
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "精神健康系统-阅读汇报.html"
EXPECTED_IDS = [
    "title", "map", "opening", "era-premodern", "era-asylum", "era-medical",
    "era-deinst", "era-transinst", "era-programs", "conclusion", "sources",
]

problems: list[str] = []
notes: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        problems.append(msg)


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return html_lib.unescape(fragment)


def slide_html(doc: str, sid: str) -> str:
    m = re.search(r'<section[^>]*data-id="' + re.escape(sid) + r'"[^>]*>(.*?)</section>', doc, re.S)
    return m.group(1) if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not HTML.exists():
        print("缺少成品：" + str(HTML), file=sys.stderr)
        return 1
    doc = HTML.read_text(encoding="utf-8")
    size = len(doc.encode("utf-8"))

    # C1 / C18
    check(size < 500 * 1024, f"C18 文件过大：{size/1024:.1f} KB（目标 <500KB）")

    # C2: 11 slides, ids, order
    ids = re.findall(r'<section[^>]*class="slide[^"]*"[^>]*data-id="([^"]+)"', doc)
    check(len(ids) == 11, f"C2 幻灯片数量为 {len(ids)}，应为 11")
    check(ids == EXPECTED_IDS, f"C2 页序不对：{ids}")
    check(len(set(ids)) == len(ids), "C2 data-id 重复")

    # C3 / C4: notes
    m = re.search(r'<script type="application/json" id="notes-data">(.*?)</script>', doc, re.S)
    check(m is not None, "C3 缺少 notes-data")
    notes_data = json.loads(m.group(1)) if m else []
    check(len(notes_data) == 11, f"C3 讲稿条数为 {len(notes_data)}，应为 11")

    def seconds(t: str) -> int:
        a, b = t.split("–")
        def p(x: str) -> int:
            mm, ss = x.split(":")
            return int(mm) * 60 + int(ss)
        return p(b) - p(a)

    total = sum(seconds(n["time"]) for n in notes_data)
    check(total == 460, f"C4 时间码合计 {total}s，应为 460s（7:40）")

    # C5: map data / static leaves
    m = re.search(r'<script type="application/json" id="map-data">(.*?)</script>', doc, re.S)
    check(m is not None, "C5 缺少 map-data")
    nodes = json.loads(m.group(1))["nodes"] if m else {}
    check(len(nodes) == 22, f"C5 map-data 节点数为 {len(nodes)}，应为 22")
    leaf_count = len(re.findall(r'<button[^>]*class="leaf[^"]*"', doc))
    check(leaf_count == 22, f"C5 静态叶子按钮为 {leaf_count}，应为 22")
    branch_counts = Counter(v["branch"] for v in nodes.values())
    check(branch_counts == Counter({"01": 4, "02": 5, "03": 6, "04": 7}), f"C5 分支计数不对：{branch_counts}")
    for nid, v in nodes.items():
        label = v.get("label", "")
        check(label in doc, f"C5 静态标签缺失：{nid} {label}")

    # C6: 6% gap
    check('class="gap"' in doc and "仅隔 6%" in doc, "C6 缺少 P2 的 6% 缺口")
    check(re.search(r"\.gap\{[^}]*height:12px", doc) is not None, "C6 6% 缺口高度不是 12px")

    # C7 / C8: page numbers
    for i in range(1, 12):
        check(f"{i:02d} / 11" in doc, f"C7 缺少页脚 {i:02d} / 11")
    for i in range(1, 7):
        check(f"{i:02d} / 06" in doc, f"C8 缺少六格页眉 {i:02d} / 06")

    # C9: rail positions
    for pct in ("0%", "18%", "36%", "62%", "68%", "90%"):
        check(f'left:{pct}' in doc, f"C9 导轨缺少刻度 {pct}")

    # C10: no external links
    check(re.search(r'\b(?:src|href)\s*=\s*["\']https?://', doc) is None, "C10 存在外链 src/href")
    check("@import" not in doc, "C10 存在 @import")
    check(re.search(r"<link\b", doc, re.I) is None, "C10 存在 link 标签")
    check(re.search(r"url\(\s*[\"']?https?://", doc) is None, "C10 存在远程 url()")

    # C11 screen banned strings
    screen = re.sub(r"<style.*?</style>", "", doc, flags=re.S)
    screen = re.sub(r"<script.*?</script>", "", screen, flags=re.S)
    screen_text = strip_tags(screen)
    for banned in ("23.4", "1844", "1892"):
        check(banned not in screen_text, f"C11 屏幕出现禁用内容：{banned}")
    p10 = strip_tags(slide_html(doc, "conclusion"))
    check("15 万" not in p10, "C11 P10 出现 15 万")
    p9 = strip_tags(slide_html(doc, "era-programs"))
    check("99%" not in p9, "C11 P9 出现 99%")
    p6 = strip_tags(slide_html(doc, "era-medical"))
    check("1844" not in p6 and "1892" not in p6, "C11 P6 出现学会之争")

    # C12 / C13 / C14 / C15: P2 summaries
    allowed = re.compile(r"(?:19|20)\d{2}(?:s|–\d{4})?|DSM-III-R|DSM-IV|DSM-III|90 年代|60 年代|20 世纪 80 年代|2000–2002")
    for nid, v in nodes.items():
        lines = v.get("lines", [])
        check(3 <= len(lines) <= 4, f"C12 {nid} 摘要为 {len(lines)} 行，应为 3–4 行")
        check(bool(v.get("source")), f"C15 {nid} 缺少出处")
        check("p." not in v.get("source", "") and "pp." not in v.get("source", ""), f"C15 {nid} 出处含页码")
        for line in lines:
            check(len(line) <= 28, f"C13 {nid} 行太长（{len(line)}）：{line}")
            check("%" not in line, f"C14 {nid} 摘要含百分比：{line}")
            rest = allowed.sub("", line)
            check(not re.search(r"\d", rest), f"C14 {nid} 摘要含统计数字：{line}")
            check("我的读法" not in line, f"C14 {nid} 摘要出现我的读法")

    # C16 / C17: no page citations / placeholders
    check("待核" not in doc, "C16 存在“待核”")
    check(re.search(r"\bp\.\d", doc) is None, "C16 存在 p.xxx 页码")
    check(re.search(r"\bpp\.\d", doc) is None, "C16 存在 pp.xxx 页码")
    for placeholder in ("TODO", "FIXME", "〔待填〕"):
        check(placeholder not in doc, f"C17 存在占位符：{placeholder}")

    # C19: print
    check("@page" in doc and "338.7mm" in doc and "190.5mm" in doc, "C19 缺少 @page 338.7×190.5mm")
    check("@media print" in doc, "C19 缺少 @media print")

    # C20: old term
    check("阅读报告" not in screen_text, "C20 屏幕仍出现“阅读报告”")

    # C21: P1/P3/P5
    p1 = slide_html(doc, "title")
    p3 = slide_html(doc, "opening")
    p5 = slide_html(doc, "era-asylum")
    check("尼采" not in p1 and "rail" not in p1, "C21 P1 出现题词或导轨")
    check("李伟烨" not in p3, "C21 P3 仍出现署名")
    check("据教材转述" in p5, "C21 P5 引文缺少“据教材转述”")

    # A8: six-grid three-piece
    for sid in ("era-premodern","era-asylum","era-medical","era-deinst","era-transinst","era-programs"):
        frag = slide_html(doc, sid)
        check('class="judge' in frag, f"A8 {sid} 缺少判断句")
        check(('class="evidence' in frag) or ('class="explain' in frag), f"A8 {sid} 缺少证据/说明")
        check('class="source' in frag, f"A8 {sid} 缺少出处")
        check('class="rail' in frag, f"A8 {sid} 缺少导轨")
    # A15: P1 credits one line
    p1credits = re.search(r'<div class="title-credits[^"]*">(.*?)</div>', p1, re.S)
    check(p1credits is not None, "A15 P1 缺少署名")
    if p1credits:
        check(p1credits.group(1).count('class="lbl"') == 3, "A15 P1 署名不是三组")
        check("<br" not in p1credits.group(1), "A15 P1 署名被拆成多行")
    # A16/P10: three columns
    p10html = slide_html(doc, "conclusion")
    check(p10html.count('class="concl-col') == 3, "P10 不是三栏")

    # 数值增长 / 数据条增长
    num_spans = re.findall(r'<span[^>]*class="[^"]*num-anim[^"]*"[^>]*>', doc)
    check(len(num_spans) >= 25, f"数值动效 span 只有 {len(num_spans)} 个，预期 25")
    for tag in num_spans:
        check('data-num=' in tag, "数值动效 span 缺少 data-num：" + tag[:80])
    p9html = slide_html(doc, "era-programs")
    check(p9html.count('data-bar=') == 2, "P9 数据条不是 2 个")
    check('transform:scaleX(var(--bar,0))' in doc, "数据条缺少 scaleX 初始态")
    check('_barAnim' in doc and 'duration:900' in doc, "数据条缺少 WAAPI .9s 增长动画")
    check('data-bar=".76"' in p9html and 'data-bar=".07"' in p9html, "P9 两个数据条目标值不对")

    # C22: P2 accessibility
    check('role="region"' in doc and "aria-live=\"polite\"" in doc, "C22 卡片缺少 role/aria-live")
    check('aria-label="关闭摘要"' in doc, "C22 关闭按钮缺少 aria-label")

    # C23: P11 counts
    idx = re.search(r'<ol class="index-list">(.*?)</ol>', doc, re.S)
    cites = re.search(r'<ol class="cite-list">(.*?)</ol>', doc, re.S)
    check(idx is not None and len(re.findall(r"<li", idx.group(1))) == 6, "C23 P11 节名索引不是 6 行")
    check(cites is not None and len(re.findall(r"<li", cites.group(1))) == 8, "C23 P11 引用不是 8 条")
    check("99%" in strip_tags(slide_html(doc, "sources")), "C23 P11 缺少 99/60 备注")

    # Extra: lang, title, notes drawer, debug hook
    check('lang="zh-CN"' in doc, "缺少 lang=zh-CN")
    check("<title>" in doc and "阅读汇报" in doc, "title 缺失或不是阅读汇报")
    check("window.__deck" in doc, "缺少 window.__deck 自检钩子")
    check("prefers-reduced-motion" in doc, "缺少 prefers-reduced-motion 兜底")
    check("html.no-js" in doc and "no-js" in doc, "缺少无 JS 兜底")

    if args.strict:
        for bad in ("待填", "待补", "draft", "DRAFT"):
            check(bad not in doc, f"strict 残留：{bad}")

    print(f"文件：{HTML.name}  {size/1024:.1f} KB")
    print(f"幻灯片 {len(ids)}，讲稿 {len(notes_data)}，P2 节点 {len(nodes)}，时间码 {total}s")
    print(f"检查项：C1–C23；问题 {len(problems)} 项")
    if problems:
        for p in problems:
            print("  ✗ " + p)
        return 1
    print("  ✓ 全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
