from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json, os, urllib.parse, urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"subscription"/"data.json"
KST=ZoneInfo("Asia/Seoul")
BASE="https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1"
KEY=os.getenv("DATA_GO_KR_API_KEY","").strip()

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_date(v):
    if not v:return None
    v=str(v).strip().replace(".","-")
    for fmt in ("%Y-%m-%d","%Y%m%d"):
        try:return datetime.strptime(v,fmt).date()
        except:pass
    return None

def val(row,*keys):
    for k in keys:
        v=row.get(k)
        if v not in (None,""):return str(v).strip()
    return ""

def fetch(endpoint,from_notice,to_notice):
    params={
        "page":1,"perPage":100,"returnType":"JSON","serviceKey":KEY,
        "cond[RCRIT_PBLANC_DE::GTE]":from_notice.isoformat(),
        "cond[RCRIT_PBLANC_DE::LTE]":to_notice.isoformat(),
    }
    url=f"{BASE}/{endpoint}?"+urllib.parse.urlencode(params)
    return get_json(url).get("data",[])

def normalize(row,kind,today):
    start=parse_date(val(row,"RCEPT_BGNDE","RCEPT_BGN_DE","GNLR_RCEPT_BGNDE","SPSPLY_RCEPT_BGNDE"))
    end=parse_date(val(row,"RCEPT_ENDDE","RCEPT_END_DE","GNLR_RCEPT_ENDDE","SPSPLY_RCEPT_ENDDE"))
    announce=parse_date(val(row,"PRZWNER_PRESNATN_DE","PRZWNER_PRESNATN_DAY"))

    if not start:
        start=parse_date(val(row,"GNLR_RCEPT_BGNDE","SPSPLY_RCEPT_BGNDE"))
    if not end:
        end=parse_date(val(row,"GNLR_RCEPT_ENDDE","SPSPLY_RCEPT_ENDDE"))

    active=bool(start and end and start<=today<=end)
    upcoming=bool(start and today<start<=today+timedelta(days=7))
    announce_today=(announce==today)
    if not (active or upcoming or announce_today):
        return None

    dday=(end-today).days if end else None
    if dday is None:dlabel=""
    elif dday==0:dlabel="D-DAY"
    elif dday>0:dlabel=f"D-{dday}"
    else:dlabel=""

    status="접수중" if active else ("접수예정" if upcoming else "접수마감")

    return {
        "type":kind,
        "name":val(row,"HOUSE_NM","HOUSE_NAME") or "단지명 미확인",
        "region":val(row,"SUBSCRPT_AREA_CODE_NM","SUBSCRPT_AREA_NM"),
        "address":val(row,"HSSPLY_ADRES","HSSPLY_ADDRESS"),
        "start":start.isoformat() if start else "",
        "end":end.isoformat() if end else "",
        "announce":announce.isoformat() if announce else "",
        "url":val(row,"PBLANC_URL","PBLANC_HMPG_ADRES","HMPG_ADRES"),
        "status":status,
        "dday":dday,
        "dday_label":dlabel,
        "today_announce":announce_today
    }

def main():
    now=datetime.now(KST);today=now.date()
    weekday="월화수목금토일"[today.weekday()]

    if not KEY:
        payload={
            "date_label":f"{today.year}년 {today.month}월 {today.day}일 {weekday}요일",
            "updated_at":now.strftime("%H:%M"),
            "counts":{"ongoing":0,"urgent":0,"announce_today":0},
            "items":[],
            "error":"DATA_GO_KR_API_KEY 미설정"
        }
        OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        print("WARNING: DATA_GO_KR_API_KEY가 없습니다.")
        return

    rows=[]
    from_notice=today-timedelta(days=60)
    to_notice=today+timedelta(days=7)

    for endpoint,kind in [
        ("getAPTLttotPblancDetail","청약"),
        ("getRemndrLttotPblancDetail","무순위"),
    ]:
        try:
            for r in fetch(endpoint,from_notice,to_notice):
                x=normalize(r,kind,today)
                if x:rows.append(x)
        except Exception as e:
            print("API ERROR",endpoint,repr(e))

    uniq={}
    for x in rows:
        uniq[(x["type"],x["name"],x["start"],x["end"])]=x
    rows=list(uniq.values())

    rows.sort(key=lambda x:(x["end"] or "9999-12-31",x["type"],x["name"]))

    payload={
        "date_label":f"{today.year}년 {today.month}월 {today.day}일 {weekday}요일",
        "updated_at":now.strftime("%H:%M"),
        "counts":{
            "ongoing":sum(1 for x in rows if x["status"]=="접수중"),
            "urgent":sum(1 for x in rows if x["status"]=="접수중" and x["dday"] is not None and x["dday"]<=1),
            "announce_today":sum(1 for x in rows if x["today_announce"])
        },
        "items":rows
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("subscription updated:",len(rows),"items")

if __name__=="__main__":
    main()
