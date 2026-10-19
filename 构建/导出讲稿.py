#!/usr/bin/env python3
"""从 HTML 的 notes-data 导出逐页讲稿 Markdown。"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "精神健康系统-阅读汇报.html"
OUT = ROOT / "讲稿-精神健康系统.md"


def main() -> int:
    doc = HTML.read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="notes-data">(.*?)</script>', doc, re.S)
    if not m:
        raise SystemExit("缺少 notes-data")
    notes = json.loads(m.group(1))
    lines = [
        "# 讲稿 · 《精神健康系统》阅读汇报",
        "",
        "> 总时长 7:40；时间码与 HTML 的 notes-data 同源。P1 不口播，P2 只停 35 秒。",
        "",
    ]
    for i, n in enumerate(notes, 1):
        lines.append(f"## P{i} · {n['title']}（{n['time']}）")
        lines.append("")
        text = n["text"]
        if "超时版：" in text:
            main, alt = text.split("超时版：", 1)
            lines.append(main.strip())
            lines.append("")
            lines.append("**超时版**：" + alt.strip())
        else:
            lines.append(text)
        if n.get("warn"):
            warn = n["warn"]
            if warn.startswith("备注："):
                warn = warn[3:]
            lines.append("")
            lines.append("> 备注：" + warn)
        lines.append("")
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"已写出 {OUT.name}（{len(notes)} 页，{len(OUT.read_text(encoding='utf-8'))} 字符）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
