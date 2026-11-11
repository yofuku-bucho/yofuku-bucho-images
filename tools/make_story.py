"""今夜のリールを予告するストーリー画像(1080x1920)を作る。
使い方: python tools/make_story.py reels/r43_rack ["今夜21時"]
reel_cover.jpg を背景に、caption.txt の1行目を問いとして大きく出し、reels/<reel>/story.jpg に保存する。
"""
import base64, html, pathlib, re, sys
from playwright.sync_api import sync_playwright

d = pathlib.Path(sys.argv[1])
when = sys.argv[2] if len(sys.argv) > 2 else "今夜21時"
first = (d / "caption.txt").read_text(encoding="utf-8").strip().splitlines()[0]
m = re.search(r"#(\d+)", (d / "caption.txt").read_text(encoding="utf-8"))
series = f"売れる店のしくみ #{m.group(1)}" if m and "売れる店のしくみ" in (d / "caption.txt").read_text(encoding="utf-8") else "洋服部長の新作リール"
q = html.escape(first).replace("、", "、<br>", 1)
bg = base64.b64encode((d / "reel_cover.jpg").read_bytes()).decode()
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@800&family=Zen+Kaku+Gothic+New:wght@700;900&family=Oswald:wght@500&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;position:relative;overflow:hidden;font-family:'Zen Kaku Gothic New';background:#1b1512}}
#bg{{position:absolute;inset:-40px;background:url(data:image/jpeg;base64,{bg}) center/cover;filter:blur(14px) brightness(.45)}}
#ph{{position:absolute;left:190px;top:430px;width:700px;height:1244px;background:url(data:image/jpeg;base64,{bg}) center/cover;border:6px solid #fff8ee;box-shadow:0 30px 80px rgba(0,0,0,.6);transform:rotate(-3deg)}}
#when{{position:absolute;top:130px;left:0;right:0;text-align:center}}
#when span{{display:inline-block;background:#8a2a35;color:#fff;font-size:56px;font-weight:900;padding:12px 40px;border-radius:60px}}
#ser{{text-align:center;color:#e8d9c4;font-family:'Oswald';font-size:36px;letter-spacing:.08em;margin-top:22px}}
#q{{position:absolute;left:60px;right:60px;top:1250px;background:rgba(255,250,242,.97);border:4px solid #3a2622;box-shadow:14px 14px 0 #8a2a35;padding:34px 30px;text-align:center}}
#q .a{{font-family:'Shippori Mincho B1';font-size:70px;line-height:1.35;color:#3a2622}}
#q .b{{font-size:34px;font-weight:700;color:#5b4540;margin-top:16px}}
#acct{{position:absolute;bottom:90px;width:100%;text-align:center;font-family:'Oswald';font-size:34px;color:#e8d9c4;letter-spacing:.14em}}
</style></head><body><div id="bg"></div><div id="ph"></div>
<div id="when"><span>{html.escape(when)} 公開</span><div id="ser">{html.escape(series)}</div></div>
<div id="q"><div class="a">{q}</div><div class="b">答えは今夜のリールで。プロフィールからどうぞ</div></div>
<div id="acct">@yofuku.bucho</div></body></html>"""
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(page, wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.screenshot(path=str(d / "story.jpg"), type="jpeg", quality=90)
    b.close()
print(d / "story.jpg")
