#!/usr/bin/env python3
"""截图 + P2 卡片/键盘/溢出测量 + contact sheet。

用法：python3 构建/截图.py
环境：CHROME_BIN 可覆盖 Chrome 路径。
"""
from __future__ import annotations

import html as html_lib
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
QA = ROOT / "qa"
CHROME = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
URL = HTML.resolve().as_uri()
UA_TAIL = ["--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions", "--disable-dev-shm-usage",
           "--in-process-gpu", "--disable-gpu-sandbox", "--force-color-profile=srgb"]


def run(args, timeout=60):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def main() -> int:
    if not Path(CHROME).exists():
        print("找不到 Chrome：" + CHROME, file=sys.stderr)
        return 1
    QA.mkdir(parents=True, exist_ok=True)
    ud = tempfile.mkdtemp(prefix="dsh-deck-")
    chrome_log = QA / "chrome.log"
    chrome_log.write_text("", encoding="utf-8")
    failures: list[str] = []

    def common():
        return [CHROME, "--headless=new", "--user-data-dir=" + ud] + UA_TAIL

    def shot(name: str, query: str, w: int = 1280, h: int = 720, scale: int = 2):
        out = QA / name
        args = common() + [
            "--window-size=" + str(w) + "," + str(h),
            "--force-device-scale-factor=" + str(scale),
            "--virtual-time-budget=4500",
            "--screenshot=" + str(out),
            URL + query,
        ]
        p = run(args)
        with chrome_log.open("a", encoding="utf-8") as f:
            f.write(p.stderr)
        if not out.exists():
            failures.append(f"截图失败：{name}")
            print("  ✗ " + name)
        else:
            print("  ✓ " + name)

    print("逐页截图：")
    for i in range(11):
        shot(f"slide-{i+1:02d}.png", f"?p={i}&instant=1&shot=1")

    print("交互截图：")
    shot("slide-02-card-deinst.png", "?p=1&instant=1&card=deinst&shot=1")
    shot("slide-02-card-whotreats.png", "?p=1&instant=1&card=whotreats&shot=1")
    shot("notes.png", "?p=7&instant=1&notes=1&shot=1")
    shot("800x600-p02.png", "?p=1&instant=1&shot=1", 800, 600)
    shot("800x600-p11.png", "?p=10&instant=1&shot=1", 800, 600)
    shot("1024x768-p08.png", "?p=7&instant=1&shot=1", 1024, 768)

    print("无 JS 兜底：")
    nojs = QA / "no-js-test.html"
    doc = HTML.read_text(encoding="utf-8")
    doc = re.sub(r"<script.*?</script>", "", doc, flags=re.S).replace('class="js"', 'class="no-js"')
    nojs.write_text(doc, encoding="utf-8")
    args = common() + ["--window-size=1280,1600", "--force-device-scale-factor=1",
                       "--virtual-time-budget=2500", "--screenshot=" + str(QA / "no-js.png"),
                       nojs.resolve().as_uri()]
    p = run(args)
    with chrome_log.open("a", encoding="utf-8") as f:
        f.write(p.stderr)
    if (QA / "no-js.png").exists():
        print("  ✓ no-js.png")
    else:
        failures.append("无 JS 截图失败")
        print("  ✗ no-js.png")

    print("QA 测量：")
    args = common() + ["--window-size=1280,720", "--virtual-time-budget=6000", "--dump-dom", URL + "?qa=1"]
    p = run(args)
    with chrome_log.open("a", encoding="utf-8") as f:
        f.write(p.stderr)
    m = re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>', p.stdout, re.S)
    if not m:
        failures.append("QA 结果缺失")
        print("  ✗ QA 结果缺失")
        qa = {}
    else:
        qa = json.loads(html_lib.unescape(m.group(1)))
        (QA / "measure.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
        (QA / "card-fit.json").write_text(json.dumps(qa.get("cards", []), ensure_ascii=False, indent=2), encoding="utf-8")
        (QA / "keyboard.json").write_text(json.dumps(qa.get("keyboard", {}), ensure_ascii=False, indent=2), encoding="utf-8")
        errors = qa.get("errors", [])
        (QA / "console.log").write_text("\n".join(errors) if errors else "no console errors\n", encoding="utf-8")
        print("  slides", qa.get("slides"), "notes", qa.get("notes"), "nodes", qa.get("nodes"))
        if qa.get("slides") != 11: failures.append("slides != 11")
        if qa.get("notes") != 11: failures.append("notes != 11")
        if qa.get("nodes") != 22: failures.append("nodes != 22")
        if qa.get("notesCount") != 11: failures.append("notesCount != 11")
        if errors: failures.append("console errors: " + "; ".join(errors))
        for item in qa.get("overflow", []):
            if item["right"] > 0.5 or item["bottom"] > 0.5:
                failures.append(f"overflow {item['id']} right={item['right']} bottom={item['bottom']}")
        for card in qa.get("cards", []):
            if card["overlap"] or not card["inside"]:
                failures.append(f"card problem {card['id']} overlap={card['overlap']} inside={card['inside']}")
            if not (3 <= card["lines"] <= 4):
                failures.append(f"card lines {card['id']} = {card['lines']}")
        expected_rails = {"era-premodern":0.0,"era-asylum":0.18,"era-medical":0.36,"era-deinst":0.62,"era-transinst":0.68,"era-programs":0.90}
        rails = qa.get("rails", [])
        if len(rails) != 6:
            failures.append("rail count = " + str(len(rails)))
        for item in rails:
            want = expected_rails.get(item["id"])
            if want is None or abs(item["ratio"] - want) > 0.015:
                failures.append(f"rail {item['id']} ratio={item['ratio']} want={want}")
        for k, v in qa.get("keyboard", {}).items():
            if not v:
                failures.append("keyboard " + k)
        if not qa.get("motionOff"):
            failures.append("motionOff false")
        if not failures:
            print("  ✓ 无溢出、22 张卡片不遮标签、键盘路径通过")
        else:
            for f in failures:
                print("  ✗ " + f)

    # A2/A3 导航 QA
    print("导航 QA：")
    args = common() + ["--window-size=1280,720", "--virtual-time-budget=6000", "--dump-dom", URL + "?qa=nav"]
    p = run(args)
    with chrome_log.open("a", encoding="utf-8") as f:
        f.write(p.stderr)
    m = re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>', p.stdout, re.S)
    if not m:
        failures.append("导航 QA 结果缺失")
        print("  ✗ 导航 QA 结果缺失")
    else:
        nav = json.loads(html_lib.unescape(m.group(1)))
        (QA / "nav.json").write_text(json.dumps(nav, ensure_ascii=False, indent=2), encoding="utf-8")
        ok = nav.get("steps") == list(range(1, 11)) and nav.get("end") == 10 and nav.get("afterEnd") == 10
        if not ok:
            failures.append("导航 QA 失败：" + json.dumps(nav, ensure_ascii=False))
            print("  ✗ " + json.dumps(nav, ensure_ascii=False))
        else:
            print("  ✓ 连按 10 次到 P11；末页停住")

    # A11 800×600 QA
    print("800×600 QA：")
    args = common() + ["--window-size=800,600", "--virtual-time-budget=6000", "--dump-dom", URL + "?qa=1"]
    p = run(args)
    with chrome_log.open("a", encoding="utf-8") as f:
        f.write(p.stderr)
    m = re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>', p.stdout, re.S)
    if not m:
        failures.append("800×600 QA 结果缺失")
        print("  ✗ 800×600 QA 结果缺失")
    else:
        qa800 = json.loads(html_lib.unescape(m.group(1)))
        (QA / "measure-800.json").write_text(json.dumps(qa800, ensure_ascii=False, indent=2), encoding="utf-8")
        bad = [x for x in qa800.get("overflow", []) if x["right"] > 0.5 or x["bottom"] > 0.5]
        bad_cards = [x for x in qa800.get("cards", []) if x["overlap"] or not x["inside"]]
        if bad or bad_cards or qa800.get("errors"):
            failures.append("800×600 QA 失败")
            print("  ✗ 800×600 有溢出/卡片/错误")
        else:
            print("  ✓ 完整可见、无滚动条、卡片不溢出")

    # 数值/数据条动效 QA
    print("数值动效 QA：")
    args = common() + ["--window-size=1280,720", "--virtual-time-budget=6000", "--dump-dom", URL + "?qa=numbers"]
    p = run(args)
    with chrome_log.open("a", encoding="utf-8") as f:
        f.write(p.stderr)
    m = re.search(r'<pre id="qa-result"[^>]*>(.*?)</pre>', p.stdout, re.S)
    if not m:
        failures.append("数值动效 QA 结果缺失")
        print("  ✗ 数值动效 QA 结果缺失")
    else:
        num = json.loads(html_lib.unescape(m.group(1)))
        (QA / "numbers.json").write_text(json.dumps(num, ensure_ascii=False, indent=2), encoding="utf-8")
        if not num.get("ok"):
            failures.append("数值动效 QA 失败：" + json.dumps(num, ensure_ascii=False))
            print("  ✗ " + json.dumps(num, ensure_ascii=False))
        else:
            print("  ✓ 76% / 1500 从 0 增长到目标；数据条 WAAPI 0.9s")

    # Contact sheet
    try:
        from PIL import Image, ImageDraw, ImageFont
        files = [QA / f"slide-{i:02d}.png" for i in range(1, 12)]
        thumb = (640, 360); pad = 16; cols = 3; rows = 4
        W = cols * thumb[0] + (cols + 1) * pad
        H = rows * thumb[1] + (rows + 1) * pad
        sheet = Image.new("RGB", (W, H), (28, 29, 32))
        d = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 22)
        except Exception:
            font = ImageFont.load_default()
        for i, f in enumerate(files):
            if not f.exists(): continue
            im = Image.open(f).convert("RGB").resize(thumb, Image.LANCZOS)
            c = i % cols; r = i // cols
            x = pad + c * (thumb[0] + pad); y = pad + r * (thumb[1] + pad)
            sheet.paste(im, (x, y))
            d.text((x + 6, y + thumb[1] + 3), f"P{i+1}", fill=(230, 230, 230), font=font)
        sheet.save(QA / "contact-sheet.png")
        print("  ✓ contact-sheet.png")
    except Exception as e:
        failures.append("contact sheet: " + str(e))
        print("  ✗ contact-sheet", e)

    shutil.rmtree(ud, ignore_errors=True)
    if failures:
        print("\n失败 " + str(len(failures)) + " 项")
        return 1
    print("\n截图与测量全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
