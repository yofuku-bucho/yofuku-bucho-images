"""明るい表紙（方眼紙＋色パネル＋透過イラスト）。使い方: python hook_cover3.py art.png "1行目<br>2行目" "English line" "#パネル色" "ラベル" out.jpg"""
import base64, io, sys
from PIL import Image
from playwright.sync_api import sync_playwright
art, text, en, panel, label, out = sys.argv[1:7]
im = Image.open(art).convert("RGBA"); im = im.crop(im.getbbox()); buf = io.BytesIO(); im.save(buf, "PNG")
u = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
CSS = """@import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@800&family=Zen+Kaku+Gothic+New:wght@700&family=Cormorant+Garamond:ital,wght@1,600&family=IBM+Plex+Mono:wght@500&display=swap');
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1920px;position:relative;overflow:hidden;color:#1F2A44;font-family:'Zen Kaku Gothic New';background-color:#F3EEE4;
 background-image:linear-gradient(rgba(31,42,68,.08) 2px,transparent 2px),linear-gradient(90deg,rgba(31,42,68,.08) 2px,transparent 2px),linear-gradient(rgba(31,42,68,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(31,42,68,.04) 1px,transparent 1px);
 background-size:120px 120px,120px 120px,24px 24px,24px 24px}
.lab{position:absolute;top:270px;left:0;right:0;text-align:center;font-family:'IBM Plex Mono','Zen Kaku Gothic New';font-size:26px;letter-spacing:.12em;color:#6b6556}
.t{position:absolute;top:330px;left:40px;right:40px;text-align:center;font-family:'Shippori Mincho B1';font-weight:800;font-size:76px;line-height:1.35}
.e{position:absolute;top:555px;left:40px;right:40px;text-align:center;font-family:'Cormorant Garamond';font-style:italic;font-weight:600;font-size:46px;color:#8E6E33}
.p{position:absolute;left:150px;right:150px;top:650px;height:900px;border-radius:36px;border:3px solid #1F2A44;box-shadow:14px 14px 0 #1F2A44;display:flex;align-items:center;justify-content:center;overflow:hidden}
.p img{max-width:82%;max-height:84%}
.a{position:absolute;top:1600px;left:0;right:0;text-align:center;font-family:'IBM Plex Mono';font-size:26px;letter-spacing:.14em;color:#6b6556}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium"); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.set_content(f'<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=lab>{label}</div><div class=t>{text}</div><div class=e>{en}</div><div class=p style="background:{panel}"><img src="{u}"></div><div class=a>@yofuku.bucho</div></body></html>', wait_until="networkidle")
    pg.evaluate("document.fonts.ready"); pg.screenshot(path=out, type="jpeg", quality=90); b.close()
