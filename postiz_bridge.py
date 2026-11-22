#!/usr/bin/env python3
"""Adaptador opcional Postiz para difusión REAL en cuentas personales autorizadas.

No confunde API aceptada con publicación: POST => SUBMITTED_UNVERIFIED hasta
confirmar permalink del proveedor. Sin credenciales => BLOCKED, sin peticiones POST.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
import amplify

ROOT=Path(__file__).resolve().parent
RECEIPTS=ROOT/"postiz_receipts.json"
BASE=os.getenv("POSTIZ_API_BASE","https://api.postiz.com/public/v1").rstrip("/")
ALLOW={s.strip() for s in os.getenv("POSTIZ_ALLOWED_INTEGRATIONS","").split(",") if s.strip()}

def auth():
    token=os.getenv("POSTIZ_API_KEY","").strip()
    if not token:
        raise RuntimeError("BLOCKED_NO_POSTIZ_API_KEY")
    if not BASE.startswith(("https://api.postiz.com/public/v1","http://127.0.0.1:","http://localhost:")):
        if not BASE.startswith("https://"):
            raise RuntimeError("BLOCKED_UNTRUSTED_POSTIZ_ENDPOINT")
    return token

def call(method,path,payload=None):
    token=auth()
    raw=json.dumps(payload,ensure_ascii=False).encode("utf-8") if payload is not None else None
    req=urllib.request.Request(BASE+path,data=raw,headers={
        "Authorization":token,"Accept":"application/json",
        "Content-Type":"application/json","User-Agent":"DenisOrganicCampaign/1.0"
    },method=method)
    try:
        with urllib.request.urlopen(req,timeout=35) as res:
            if not 200<=res.status<300:
                raise RuntimeError("FAIL_POSTIZ_HTTP_"+str(res.status))
            return json.loads(res.read(300000).decode("utf-8"))
    except urllib.error.HTTPError as e:
        # No tokens in log, only status and a short provider response.
        raise RuntimeError(f"FAIL_POSTIZ_HTTP_{e.code}") from None

def channels():
    data=call("GET","/integrations")
    if not isinstance(data,list):raise RuntimeError("FAIL_POSTIZ_UNKNOWN_INTEGRATION_SHAPE")
    return [{
        "id":str(item.get("id") or ""),
        "name":str(item.get("name") or ""),
        "network":str(item.get("identifier") or ""),
        "disabled":bool(item.get("disabled")),
        "explicitly_approved":str(item.get("id")) in ALLOW
    } for item in data if isinstance(item,dict)]

def prepare_payload(channel_id):
    text="Si te gusta entrenar desde casa, mira este momento de Denis en Tenerife 💪\n"+amplify.VIDEO
    return {
       "type":"now", "date":dt.datetime.now(dt.timezone.utc).isoformat(),
       "shortLink":False, "tags":[],
       "posts":[{
          "integration":{"id":channel_id},
          "value":[{"content":text,"image":[]}],
          "settings":{"__type":"bluesky"}
       }]
    }

def publish(integration_id,execute=False):
    if integration_id not in ALLOW:
        return {"state":"BLOCKED_UNAPPROVED_PERSONAL_CHANNEL","integration_id":integration_id}
    try:connected=channels()
    except RuntimeError as err:return {"state":str(err)}
    target=next((x for x in connected if x["id"]==integration_id),None)
    if not target or target["disabled"]:
        return {"state":"BLOCKED_PERSONAL_CHANNEL_NOT_CONNECTED"}
    # Solo texto + URL, nunca mandar a Instagram/TikTok (requieren video nuevo).
    if target["network"]!="bluesky":
        return {"state":"BLOCKED_PROVIDER_SETTINGS_UNAUDITED","network":target["network"]}
    body=prepare_payload(integration_id)
    if not execute:
        return {"state":"PASS_DRY_RUN_ONLY","integration_id":integration_id,
                "text":body["posts"][0]["value"][0]["content"],
                "would_publish":True,"published":False}
    old=amplify.read_json(RECEIPTS,{"items":[]})
    if any(r.get("integration_id")==integration_id and r.get("state") in
           ("SUBMITTED_UNVERIFIED","PROVIDER_CONFIRMED_UNVERIFIED") for r in old["items"]):
        return {"state":"BLOCKED_DUPLICATE_UNRESOLVED_SUBMISSION"}
    # Guardar intención previa para evitar duplicación si la llamada se interrumpe.
    key=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+integration_id
    rec={"id":key,"integration_id":integration_id,"state":"SUBMISSION_STARTED_NO_ACK",
         "video":amplify.VIDEO,"permalink":None,"at_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
    old["items"].append(rec)
    amplify.write_json(RECEIPTS,old)
    try:
        result=call("POST","/posts",body)
        rec["state"]="SUBMITTED_UNVERIFIED"
        rec["provider_response"]=result
    except RuntimeError as err:
        rec["state"]=str(err)
    amplify.write_json(RECEIPTS,old)
    return {"state":rec["state"],"integration_id":integration_id,
            "published_verified":False,"permalink":None,
            "note":"Postiz returned data, but release URL/public page has not been verified."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("channels","dry-run","publish"))
    p.add_argument("--integration-id",default="")
    a=p.parse_args()
    if a.action=="channels":
        try:r={"state":"PASS_AUTHENTICATED_CHANNEL_LIST","channels":channels()}
        except RuntimeError as e:r={"state":str(e),"channels":[]}
    else:r=publish(a.integration_id,execute=a.action=="publish")
    print(json.dumps(r,ensure_ascii=False))
    if r.get("state","").startswith("FAIL"):
        raise SystemExit(1)
if __name__=="__main__":main()
