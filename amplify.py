#!/usr/bin/env python3
"""Amplificador orgánico de UN video TikTok existente. 0 bots, 0 compras, 0 falsas publicaciones.

Prepara una microsite pública para compartir ese vídeo y enlaces a compositores oficiales.
La generación de enlaces nunca cuenta como distribución, clic, reproducción ni seguidor.
"""
from __future__ import annotations
import argparse
import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "site"
DATA = ROOT / "campaign.json"
MATRIX = ROOT / "distribution.json"
REPORT = ROOT / "report.json"
OWNER = "dedavid22"
REPO = "tiktok-video-amplifier"
PUBLIC_SITE = f"https://{OWNER}.github.io/{REPO}/"
VIDEO = "https://www.tiktok.com/@dedavid22/video/7710983123021974816"
ALLOWED_CHANNELS = ("whatsapp", "telegram", "x", "bluesky", "reddit", "email")
UA = "Mozilla/5.0 (compatible; DenisOrganicVideoVerifier/1.0; read-only)"

def safe_video(url: str) -> tuple[str, str]:
    """Never redirect to another creator or to an arbitrary destination."""
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname not in {"www.tiktok.com", "tiktok.com"}:
        raise ValueError("BLOCKED: only HTTPS TikTok canonical URLs")
    m = re.fullmatch(r"/@dedavid22/(video|photo)/(\d{15,22})/?", p.path)
    if not m or p.username or p.password or p.port:
        raise ValueError("BLOCKED: video must belong to @dedavid22 and use a numeric ID")
    return f"https://www.tiktok.com/@dedavid22/{m.group(1)}/{m.group(2)}", m.group(2)

def share_targets(video: str) -> dict[str, str]:
    """Share TikTok URL directly, not a tracking interstitial that adds friction."""
    msg = "Mira este vídeo de Denis en TikTok 💪"
    enc_video = urllib.parse.quote(video, safe="")
    enc_msg = urllib.parse.quote(msg + " " + video, safe="")
    txt = urllib.parse.quote(msg, safe="")
    return {
        "whatsapp": "https://api.whatsapp.com/send?text="+enc_msg,
        "telegram": "https://t.me/share/url?url="+enc_video+"&text="+txt,
        "x": "https://twitter.com/intent/tweet?text="+txt+"&url="+enc_video,
        "bluesky": "https://bsky.app/intent/compose?text="+enc_msg,
        "reddit": "https://www.reddit.com/submit?url="+enc_video+"&title="+txt,
        "email": "mailto:?subject="+urllib.parse.quote("Vídeo de Denis en TikTok",safe="")+"&body="+enc_msg,
    }

def read_json(path, default=None):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError,json.JSONDecodeError):return default

def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temp.replace(path)

def generate(video_url: str = VIDEO):
    url, video_id = safe_video(video_url)
    PAGE.mkdir(parents=True, exist_ok=True)
    old=read_json(DATA,{})
    campaign={
       "id":"personal-"+video_id,
       "owner":OWNER,"video_id":video_id,"canonical_video_url":url,
       "public_landing_url":PUBLIC_SITE,
       "created_at_utc":old.get("created_at_utc") or dt.datetime.now(dt.timezone.utc).isoformat(),
       "cost_eur":0,
       "notes":"Compartir enlaces o desplegar una web NO implica tráfico real.",
       "published_to_social_verified":old.get("published_to_social_verified",[]),
    }
    write_json(DATA,campaign)
    shares=share_targets(url)
    prev=read_json(MATRIX,{}).get("channels",{})
    channels={}
    for name, link in shares.items():
        oldrec=prev.get(name,{})
        channels[name]={
           "intent_url":link,
           "state":oldrec.get("state") if oldrec.get("state")=="PUBLISHED_VERIFIED" else "READY_COMPOSER_ONLY",
           "permalink_verified":oldrec.get("permalink_verified") if oldrec.get("state")=="PUBLISHED_VERIFIED" else None,
           "clicks_real":None, "views_attributed":None,
           "notes":"Solo abre una ventana para compartir. Se requiere cuenta y envío real."
        }
    write_json(MATRIX,{"video":url,"channels":channels,"verified_social_posts":sum(x["state"]=="PUBLISHED_VERIFIED" for x in channels.values())})
    esc=lambda s:html.escape(s,quote=True)
    cards="".join(
       "<a class='share' href='"+esc(shares[name])+"' target='_blank' rel='noopener noreferrer'>Compartir por "+esc(name.capitalize())+"</a>"
       for name in ALLOWED_CHANNELS)
    document="""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow">
<title>Denis en TikTok · Entrenamiento en casa</title>
<meta name="description" content="Un vídeo real de Denis entrenando desde casa en Tenerife. Mira el vídeo original en TikTok y compártelo si te gusta.">
<meta property="og:type" content="website">
<meta property="og:title" content="Denis · Así disfruto entrenando en casa">
<meta property="og:description" content="Una rutina, una sonrisa y un momento personal. Ver el vídeo original de TikTok.">
<meta property="og:url" content="""+esc(PUBLIC_SITE)+"""">
<meta property="og:site_name" content="Denis TikTok">
<meta name="theme-color" content="#101927">
<style>*,*:before,*:after{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 80% 0,#283d50,#101927 57%);color:#f3f6fb;
font:16px/1.6 system-ui,-apple-system,Segoe UI,Arial;min-height:100vh;padding:32px 18px}
main{max-width:720px;margin:auto}header{display:flex;gap:12px;align-items:center}
.logo{font-weight:900;border:2px solid #c9eeff;border-radius:14px;padding:5px 15px}h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.14;margin:32px 0 12px}
p{color:#d1dde8}.hero{background:#20344a;border:1px solid #52708b;border-radius:18px;padding:28px}
.cta{display:block;padding:18px 22px;border-radius:12px;background:#fbf9f4;color:#092032;text-align:center;font-weight:900;
text-decoration:none;font-size:1.16rem;margin:20px 0}.sharegrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:10px}
.share{padding:12px 9px;border:1px solid #688099;border-radius:10px;text-align:center;text-decoration:none;color:#e3f6ff;background:#1b3043}
small{color:#b4c5d7;display:block;margin-top:24px}a:focus-visible{outline:3px solid #ffce6d}</style></head>
<body><main><header><span class="logo">DENIS</span><span>🇻🇪 · Tenerife 🇮🇨</span></header>
<h1>Porque el domingo también se entrena 💪</h1>
<div class="hero"><p>Entrenando desde casa, a mi ritmo y disfrutando de lo que me gusta.</p>
<a class="cta" href="""+esc(url)+""" rel="noopener noreferrer">▶ Ver vídeo original en TikTok</a>
<p>Si te gusta, puedes compartirlo con alguien que también disfrute mantenerse activo.</p></div>
<h2>Compartir el vídeo</h2><div class="sharegrid">"""+cards+"""</div>
<small>Todos los botones abren servicios oficiales para compartir. No venden seguidores,
no crean reproducciones falsas ni publican automáticamente. Comparte solo donde sea pertinente.</small>
<p><a href="""+esc(f"https://www.tiktok.com/@{OWNER}")+""" style="color:#b8e7ff">Ver el perfil de Denis</a></p></main></body></html>"""
    (PAGE/"index.html").write_text(document,encoding="utf-8")
    (PAGE/".nojekyll").write_text("",encoding="utf-8")
    report={"generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "video_url":url,"static_site":"PASS_LOCAL_FILE_EXISTS",
      "landing_public":"BLOCKED_UNTIL_HTTP_200_AND_CONTENT_MATCH",
      "social_publications":"BLOCKED_NOT_CONNECTED",
      "social_published_verified":sum(x["state"]=="PUBLISHED_VERIFIED" for x in channels.values()),
      "real_visitors":None,"real_video_views_attributed":None,"followers_from_campaign":None,
      "status":"READY_NOT_DISTRIBUTED",
      "rules":"PASS no significa viral; contenido generado y enlaces listos no prueban visitas."
    }
    write_json(REPORT,report)
    print(json.dumps(report,ensure_ascii=False))
    return report

def verify_public(video_url=VIDEO, landing_url=PUBLIC_SITE, check_site=True):
    url, video_id=safe_video(video_url)
    results={"video":"BLOCKED_UNVERIFIED","landing":"BLOCKED_UNVERIFIED",
             "actual_distribution":"BLOCKED_NO_VERIFIED_POSTS","visits_real":None}
    profile="https://www.tiktok.com/embed/@dedavid22"
    try:
        req=urllib.request.Request(profile,headers={"User-Agent":UA})
        with urllib.request.urlopen(req,timeout=18) as res:
            raw=res.read(850000).decode("utf-8","replace")
            results["profile_http"]=res.status
        m=re.search(r'<script[^>]*id="__FRONTITY_CONNECT_STATE__"[^>]*>(.*?)</script>',raw,re.I|re.S)
        if m:
            state=json.loads(m.group(1))
            user=state.get("source",{}).get("data",{}).get("/embed/@dedavid22",{})
            vids=user.get("videoList",[])
            if user.get("userInfo",{}).get("uniqueId")=="dedavid22" and any(
              str(v.get("id"))==video_id and v.get("authorUniqueId")=="dedavid22" for v in vids):
                results["video"]="PASS_PUBLIC_VIDEO_BELONGS_TO_OWNER"
            else: results["video"]="BLOCKED_VIDEO_NOT_IN_PUBLIC_EMBED_SAMPLE"
        else:results["video"]="BLOCKED_UNAVAILABLE_PROFILE_METADATA"
    except Exception as exc:results["video"]="BLOCKED_PROFILE_FETCH_"+type(exc).__name__
    if check_site:
        try:
            req=urllib.request.Request(landing_url,headers={"User-Agent":UA})
            with urllib.request.urlopen(req,timeout=18) as res:
                raw=res.read(200000).decode("utf-8","replace")
                results["landing_http"]=res.status
            if res.status==200 and url in html.unescape(raw) and "Compartir el vídeo" in raw:
                results["landing"]="PASS_PUBLIC_HTTP_200_WITH_CORRECT_VIDEO"
            else: results["landing"]="FAIL_PUBLIC_CONTENT_MISMATCH"
        except Exception as exc:results["landing"]="BLOCKED_SITE_FETCH_"+type(exc).__name__
    matrix=read_json(MATRIX,{})
    verified=[v for v in matrix.get("channels",{}).values() if v.get("state")=="PUBLISHED_VERIFIED" and v.get("permalink_verified")]
    if verified:
        results["actual_distribution"]="UNVERIFIED_LEDGER_NEEDS_EXTERNAL_CHECK"
    results["checked_at_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    results["real_visits_cannot_be_measured_by_static_github_pages"]=True
    write_json(ROOT/"verification.json",results)
    print(json.dumps(results,ensure_ascii=False))
    return results

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=("generate","verify","verify-local"))
    ap.add_argument("--video-url",default=VIDEO)
    args=ap.parse_args()
    if args.action=="generate":generate(args.video_url)
    else:
        r=verify_public(args.video_url,check_site=args.action=="verify")
        if r["video"].startswith("FAIL") or r["landing"].startswith("FAIL"):
            raise SystemExit(1)
if __name__=="__main__":
    main()
