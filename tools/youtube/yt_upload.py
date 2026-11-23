"""Yofuku Bucho Uploader: upload the owner's own video to the owner's YouTube channel.

Usage:
  python yt_upload.py auth-url                 # print the Google sign-in URL
  python yt_upload.py auth-code "<redirect URL or code>"   # save the token
  python yt_upload.py upload video.mp4 "title" "description" [private|unlisted|public] [publishAt ISO8601]
Env: YT_CLIENT_SECRET (path to client JSON), YT_TOKEN (path to token JSON)
"""
import json, os, sys, urllib.parse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SECRET = os.environ.get("YT_CLIENT_SECRET", "client_secret.json")
TOKEN = os.environ.get("YT_TOKEN", "token.json")
REDIRECT = "http://localhost:8765/"

def flow():
    f = Flow.from_client_secrets_file(SECRET, scopes=SCOPES, redirect_uri=REDIRECT)
    return f

def creds():
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not c.valid:
        c.refresh(Request())
        open(TOKEN, "w").write(c.to_json())
    return c

def main():
    cmd = sys.argv[1]
    if cmd == "auth-url":
        url, _ = flow().authorization_url(access_type="offline", prompt="consent")
        print(url)
    elif cmd == "auth-code":
        arg = sys.argv[2]
        code = urllib.parse.parse_qs(urllib.parse.urlparse(arg).query).get("code", [arg])[0]
        f = flow(); f.fetch_token(code=code)
        open(TOKEN, "w").write(f.credentials.to_json()); print("token saved")
    elif cmd == "upload":
        path, title, desc = sys.argv[2:5]
        privacy = sys.argv[5] if len(sys.argv) > 5 else "private"
        status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
        if len(sys.argv) > 6:
            status.update(privacyStatus="private", publishAt=sys.argv[6])
        yt = build("youtube", "v3", credentials=creds())
        body = {"snippet": {"title": title, "description": desc, "categoryId": "27"}, "status": status}
        req = yt.videos().insert(part="snippet,status", body=body,
                                 media_body=MediaFileUpload(path, chunksize=-1, resumable=True))
        resp = None
        while resp is None:
            _, resp = req.next_chunk()
        print(json.dumps({"id": resp["id"], "url": "https://youtu.be/" + resp["id"], "status": resp["status"]}))

if __name__ == "__main__":
    main()
