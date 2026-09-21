#!/usr/bin/env python3
"""重建《社区文明观-阅读汇报》成品并复核。

用法（在项目根目录）：python3 build/重建.py

管线：源文件 build/deck-src-未内嵌图片.html（图片位置写占位符，现在只剩 __CANA__ 一张）
  → 从上一版成品里取出对应的内嵌图，重新替换回占位符
  → 写出 社区文明观-阅读汇报.html（自包含单文件）
  → 用无头 Chrome 重导 社区文明观-阅读汇报.pdf（@page 1280×720px，故 PDF 为 960×540pt / 14 页）
  → 复核：占位符残留、内嵌图数量、逐页横向/纵向溢出、PDF 页数

先改源文件，再跑这个脚本；不要直接改成品 HTML——下次重建会覆盖。
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import datetime
import hashlib
import json

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "build" / "deck-src-未内嵌图片.html"
OUT = ROOT / "社区文明观-阅读汇报.html"
PDF = ROOT / "社区文明观-阅读汇报.pdf"
FINGERPRINT = ROOT / "build" / "成品指纹.json"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

MEASURE_JS = """
<script>
window.addEventListener('load',function(){
  // 先把所有动画定格到终态再量：入场动画是 fill:'both' + delay 的 WAAPI，
  // 测量时若还停在延迟段，元素会被首帧的 translateY(10px) 顶到画面外，
  // 报出根本不存在的「纵溢」（封面信箱贴到画面底边时踩过一次）。
  document.getAnimations().forEach(function(a){ try{a.finish();}catch(e){} });
  var stage=document.getElementById('stage'); stage.style.transform='none';
  var out=[];
  document.querySelectorAll('.slide').forEach(function(sl,i){
    sl.style.display='flex'; sl.style.visibility='visible'; sl.style.opacity='1';
    var r=sl.getBoundingClientRect();
    var mx=0,my=0,who='';
    sl.querySelectorAll('*').forEach(function(el){
      if(el.classList.contains('notes'))return;
      var b=el.getBoundingClientRect();
      if(b.width===0&&b.height===0)return;
      var dx=b.right-r.right, dy=b.bottom-r.bottom;
      if(dx>mx){mx=dx;}
      if(dy>my){my=dy;who=(el.className||el.tagName)+' :: '+(el.textContent||'').slice(0,40);}
    });
    var ov=(sl.scrollHeight-sl.clientHeight);
    out.push(i+'|横溢'+mx.toFixed(1)+'|纵溢'+my.toFixed(1)+'|scrollH-clientH='+ov+'|'+who);
  });
  document.title='QA::'+out.join(' ;; ');
});
</script>
</body>"""


def main() -> int:
    if not pathlib.Path(CHROME).exists():
        print("找不到 Google Chrome，无法导出 PDF 与测量溢出", file=sys.stderr)
        return 1

    src = SRC.read_text(encoding="utf-8")
    # 占位符按需处理：封面底图已于 2026-09-21 按用户要求删除，__COVER__ 不再出现；
    # 以后若再加图，只要在源里写回占位符即可，脚本不必改。
    wanted = [t for t in ("__COVER__", "__CANA__") if t in src]
    if not wanted:
        print("源文件里一个图片占位符都没有，不必重建", file=sys.stderr)
        return 1

    prev = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    found = {
        "__COVER__": re.search(r"background-image:url\('(data:image/[^']+)'\)", prev),
        "__CANA__": re.search(r'src="(data:image/[^"]+)"', prev),
    }
    missing = [t for t in wanted if not found[t]]
    if missing:
        print(f"上一版成品里取不到内嵌图 {missing}，停止", file=sys.stderr)
        return 1

    out = src
    for token in wanted:
        out = out.replace(token, found[token].group(1))
    OUT.write_text(out, encoding="utf-8")
    print(f"成品已写出：{OUT.name}（{len(out):,} 字符，内嵌图 {out.count('data:image')} 张，"
          f"占位符残留 {out.count('__COVER__') + out.count('__CANA__')}）")

    with tempfile.TemporaryDirectory() as tmp:
        measure = pathlib.Path(tmp) / "measure.html"
        shutil.copy(OUT, measure)
        html = measure.read_text(encoding="utf-8", errors="surrogateescape")
        measure.write_text(html.replace("</body>", MEASURE_JS, 1), encoding="utf-8",
                           errors="surrogateescape")
        dom = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=8000", "--window-size=1400,900",
             "--dump-dom", f"file://{measure}"],
            capture_output=True, text=True).stdout
        m = re.search(r"<title>QA::(.*?)</title>", dom, re.S)
        if not m:
            print("溢出测量失败（拿不到测量结果）", file=sys.stderr)
        else:
            rows = m.group(1).split(" ;; ")
            bad = [r for r in rows if not re.search(r"横溢0\.0\|纵溢0\.0\|scrollH-clientH=0", r)]
            print(f"逐页溢出：{len(rows)} 页，异常 {len(bad)} 页")
            for r in bad:
                print("  ⚠ " + r)

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=12000", "--no-pdf-header-footer",
         f"--print-to-pdf={PDF}", f"file://{OUT}"],
        capture_output=True, text=True)
    info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
    pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
    size = re.search(r"^Page size:\s+(.+)$", info, re.M)
    print(f"PDF 已重导：{pages.group(1) if pages else '?'} 页，"
          f"{size.group(1).strip() if size else '?'}")

    # 记下这次导出时的内容指纹：检查脚本据此判断成品与 PDF 是否还是同一版本
    # （用内容而不是时间戳，git checkout 复原文件后不会误报）
    FINGERPRINT.write_text(json.dumps({
        "html_sha256": sha256(OUT),
        "pdf_sha256": sha256(PDF),
        "exported_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"指纹已记录：build/成品指纹.json")
    print("注意：本次改动若涉及页码或引文，请先用 pdftotext 核对 PDF 文字再交付。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
