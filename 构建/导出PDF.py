#!/usr/bin/env python3
"""导出 11 页 PDF，并做页数/尺寸/空白页/深色页/缺字检查。

用法：python3 构建/导出PDF.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "精神健康系统-阅读汇报.html"
PDF = ROOT / "精神健康系统-阅读汇报.pdf"
QA = ROOT / "qa" / "pdf"
CHROME = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
URL = HTML.resolve().as_uri()


def run(args, timeout=120):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def main() -> int:
    if not Path(CHROME).exists():
        print("找不到 Chrome：" + CHROME, file=sys.stderr)
        return 1
    if shutil.which("pdfinfo") is None or shutil.which("pdftoppm") is None:
        print("缺少 pdfinfo/pdftoppm", file=sys.stderr)
        return 1
    QA.mkdir(parents=True, exist_ok=True)
    for old in QA.glob("page-*.png"):
        old.unlink()
    ud = tempfile.mkdtemp(prefix="dsh-pdf-")
    args = [CHROME, "--headless=new", "--user-data-dir=" + ud,
            "--disable-gpu", "--no-sandbox", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--disable-dev-shm-usage", "--force-color-profile=srgb",
            "--virtual-time-budget=15000", "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer", "--print-to-pdf=" + str(PDF), URL]
    p = run(args)
    (QA / "chrome.log").write_text(p.stderr, encoding="utf-8")
    shutil.rmtree(ud, ignore_errors=True)
    if not PDF.exists():
        print("PDF 未生成", file=sys.stderr)
        return 1

    info = run(["pdfinfo", str(PDF)]).stdout
    pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
    size = re.search(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", info, re.M)
    page_count = int(pages.group(1)) if pages else -1
    width = float(size.group(1)) if size else 0
    height = float(size.group(2)) if size else 0
    log = []
    log.append(f"pages={page_count} size={width}x{height}pt")
    ok = True
    if page_count != 11:
        log.append("ERROR: pages != 11")
        ok = False
    if abs(width - 960) > 2 or abs(height - 540) > 2:
        log.append("ERROR: page size is not 960x540pt")
        ok = False

    r = run(["pdftoppm", "-r", "96", "-png", str(PDF), str(QA / "page")])
    log.append("pdftoppm: " + (r.stderr.strip() or "ok"))
    try:
        from PIL import Image, ImageStat
    except Exception as e:
        log.append("Pillow unavailable: " + str(e))
        (QA / "check.log").write_text("\n".join(log), encoding="utf-8")
        print("\n".join(log))
        return 1
    palette = {}
    for i in range(1, 12):
        f = QA / f"page-{i:02d}.png"
        if not f.exists():
            log.append(f"ERROR: missing {f.name}")
            ok = False
            continue
        im = Image.open(f).convert("RGB")
        stat = ImageStat.Stat(im.convert("L"))
        std = stat.stddev[0]
        corner = im.getpixel((8, 8))
        palette[f"P{i}"] = {"size": im.size, "stddev": round(std, 2), "corner": corner}
        log.append(f"P{i}: {im.size[0]}x{im.size[1]} stddev={std:.1f} corner={corner}")
        if std < 3:
            log.append(f"ERROR: P{i} looks blank")
            ok = False
        if i in (1, 3, 10):
            if sum(corner) > 180:
                log.append(f"ERROR: P{i} dark background faded")
                ok = False
        else:
            if sum(corner) < 600:
                log.append(f"ERROR: P{i} paper background too dark")
                ok = False
    (QA / "palette.json").write_text(json.dumps(palette, ensure_ascii=False, indent=2), encoding="utf-8")

    text = run(["pdftotext", "-layout", str(PDF), "-"]).stdout
    for key in ("精神健康系统", "去机构化之后", "我们不是没有方案", "敏还会回来"):
        if key not in text:
            log.append("ERROR: PDF text missing: " + key)
            ok = False
    if "23.4" in text:
        log.append("WARN: PDF text contains 23.4（检查是否只出现在讲稿备注）")
    if "阅读报告" in text:
        log.append("ERROR: PDF contains 阅读报告")
        ok = False

    log.append(f"PDF size={PDF.stat().st_size/1024:.1f} KB")
    log.append("RESULT: " + ("PASS" if ok else "FAIL"))
    (QA / "check.log").write_text("\n".join(log), encoding="utf-8")
    print("\n".join(log))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
