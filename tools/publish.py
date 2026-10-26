"""Instagramにカルーセル投稿する。
使い方: python tools/publish.py posts/001_trench [--story]
  python tools/publish.py reels/001_flow --reel  （reel.mp4 と caption.txt をリールとして投稿）
  --story を付けると、投稿のあとに story.jpg をストーリーにも出す
必要な環境変数: IG_ACCESS_TOKEN, IG_USER_ID
画像はこのリポジトリ(main、または IG_IMAGE_REF で指定したブランチ)に push 済みで、raw.githubusercontent.com から公開されている前提。
"""
import json, os, sys, time, pathlib, urllib.parse, urllib.request

API = "https://graph.instagram.com/" + os.environ.get("IG_API_VERSION", "v22.0")
RAW = "https://raw.githubusercontent.com/yofuku-bucho/yofuku-bucho-images/" + os.environ.get("IG_IMAGE_REF", "main") + "/"
TOKEN = os.environ["IG_ACCESS_TOKEN"]
USER = os.environ["IG_USER_ID"]

def call(path, params, method="POST"):
    params = dict(params, access_token=TOKEN)
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    req = urllib.request.Request(url, data=data) if method == "POST" else urllib.request.Request(url + "?" + data.decode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code}: {e.read().decode()}")

def wait_ready(cid, tries=30):
    for _ in range(tries):
        st = call(cid, {"fields": "status_code"}, method="GET").get("status_code")
        if st == "FINISHED":
            return
        if st == "ERROR":
            sys.exit(f"container {cid} failed")
        time.sleep(5)
    sys.exit(f"container {cid} timed out")

def publish_reel(d):
    caption = (d / "caption.txt").read_text(encoding="utf-8").strip()
    params = {"media_type": "REELS", "video_url": RAW + (d / "reel.mp4").as_posix(), "caption": caption, "share_to_feed": "true"}
    if (d / "reel_cover.jpg").exists():
        params["cover_url"] = RAW + (d / "reel_cover.jpg").as_posix()
    r = call(f"{USER}/media", params)
    wait_ready(r["id"], tries=120)
    pub = call(f"{USER}/media_publish", {"creation_id": r["id"]})
    print(json.dumps({"published_media_id": pub.get("id"), "reel": d.name}))

def main(post_dir, with_story=False):
    d = pathlib.Path(post_dir)
    slides = sorted(d.glob("slide_*.jpg"))
    caption = (d / "caption.txt").read_text(encoding="utf-8").strip()
    children = []
    for s in slides:
        r = call(f"{USER}/media", {"image_url": RAW + s.as_posix(), "is_carousel_item": "true"})
        children.append(r["id"])
    for c in children:
        wait_ready(c)
    carousel = call(f"{USER}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})
    wait_ready(carousel["id"])
    pub = call(f"{USER}/media_publish", {"creation_id": carousel["id"]})
    result = {"published_media_id": pub.get("id"), "post": d.name}
    if with_story:
        st = call(f"{USER}/media", {"image_url": RAW + (d / "story.jpg").as_posix(), "media_type": "STORIES"})
        wait_ready(st["id"])
        result["story_media_id"] = call(f"{USER}/media_publish", {"creation_id": st["id"]}).get("id")
    print(json.dumps(result))

if __name__ == "__main__":
    if "--reel" in sys.argv[2:]:
        publish_reel(pathlib.Path(sys.argv[1]))
    else:
        main(sys.argv[1], "--story" in sys.argv[2:])
