from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, os, re, html, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from korean_lunar_calendar import KoreanLunarCalendar

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data.json"
KST = ZoneInfo("Asia/Seoul")

CITIES = {
    "서울": (37.5665,126.9780), "인천": (37.4563,126.7052), "수원": (37.2636,127.0286),
    "춘천": (37.8813,127.7298), "강릉": (37.7519,128.8761), "청주": (36.6424,127.4890),
    "대전": (36.3504,127.3845), "세종": (36.4800,127.2890), "전주": (35.8242,127.1480),
    "광주": (35.1595,126.8526), "대구": (35.8714,128.6014), "부산": (35.1796,129.0756),
    "울산": (35.5384,129.3114), "창원": (35.2285,128.6811), "제주": (33.4996,126.5312)
}

ZODIAC = [
    ("쥐띠",[96,84,72,60,48,36]), ("소띠",[97,85,73,61,49,37]), ("범띠",[98,86,74,62,50,38]),
    ("토끼띠",[99,87,75,63,51,39]), ("용띠",[0,88,76,64,52,40]), ("뱀띠",[1,89,77,65,53,41]),
    ("말띠",[2,90,78,66,54,42]), ("양띠",[3,91,79,67,55,43]), ("원숭이띠",[4,92,80,68,56,44]),
    ("닭띠",[5,93,81,69,57,45,33]), ("개띠",[6,94,82,70,58,46,34]), ("돼지띠",[95,83,71,59,47,35])
]
FORTUNE_SENTENCES = [
    "서두르기보다 순서를 지키면 원하는 흐름을 만들 수 있다.",
    "작은 기회도 가볍게 넘기지 말고 차분히 살펴보는 것이 좋다.",
    "주변의 조언을 열린 마음으로 들으면 생각지 못한 해답이 보인다.",
    "미뤄둔 일을 하나씩 정리하면 마음까지 한결 가벼워진다.",
    "말 한마디가 분위기를 바꿀 수 있으니 부드러운 표현을 선택하라.",
    "익숙한 방법보다 새로운 시도가 좋은 변화를 불러올 수 있다.",
    "금전 문제는 충동적인 결정보다 한 번 더 확인하는 태도가 유리하다.",
    "몸의 신호를 무시하지 말고 충분한 휴식과 수분을 챙겨라.",
    "가까운 사람과의 대화에서 좋은 기운과 아이디어를 얻을 수 있다.",
    "지금까지 쌓아온 노력이 작은 성과로 이어지기 시작하는 날이다.",
    "무리하게 앞서가기보다 자신의 페이스를 지키는 것이 중요하다.",
    "예상 밖의 연락이나 소식이 새로운 계기가 될 수 있다."
]

def get_json(url, headers=None):
    req=urllib.request.Request(url, headers=headers or {"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def weather_emoji(code):
    if code == 0: return "☀️"
    if code in (1,2): return "🌤️"
    if code == 3: return "☁️"
    if code in (45,48): return "🌫️"
    if code in (51,53,55,56,57): return "🌦️"
    if code in (61,63,65,66,67,80,81,82): return "🌧️"
    if code in (71,73,75,77,85,86): return "🌨️"
    if code in (95,96,99): return "⛈️"
    return "☁️"

def weather_text(now):
    weekday="월화수목금토일"[now.weekday()]
    lines=[f"{now:%Y년 %-m월 %-d일} {weekday}요일", "❒ 지역별 날씨전망 ❒", ""]
    for name,(lat,lon) in CITIES.items():
        q=urllib.parse.urlencode({
            "latitude":lat,"longitude":lon,
            "hourly":"weather_code",
            "daily":"temperature_2m_max,temperature_2m_min",
            "timezone":"Asia/Seoul","forecast_days":1
        })
        j=get_json("https://api.open-meteo.com/v1/forecast?"+q)
        times=j["hourly"]["time"]; codes=j["hourly"]["weather_code"]
        morning_key=now.strftime("%Y-%m-%d")+"T08:00"
        afternoon_key=now.strftime("%Y-%m-%d")+"T15:00"
        mcode=codes[times.index(morning_key)] if morning_key in times else codes[8]
        acode=codes[times.index(afternoon_key)] if afternoon_key in times else codes[15]
        lo=round(j["daily"]["temperature_2m_min"][0]); hi=round(j["daily"]["temperature_2m_max"][0])
        lines.append(f"✫{name}({weather_emoji(mcode)})➠({weather_emoji(acode)})  {lo}℃ ~ {hi}℃")
    return "\n".join(lines)

def fortune_text(now):
    cal=KoreanLunarCalendar()
    cal.setSolarDate(now.year, now.month, now.day)
    gapja=cal.getGapJaString()
    # ex: "병오년 정유월 신사일"
    day_ganji=""
    m=re.search(r"([가-힣]{2})일", gapja)
    if m: day_ganji=m.group(1)
    title=f"오늘의 운세, {now.month}월 {now.day}일"
    lines=[title,"",f"[음력 {cal.lunarMonth}월 {cal.lunarDay}일] 일진: {day_ganji}",""]
    seed=now.year*10000+now.month*100+now.day
    for idx,(name,years) in enumerate(ZODIAC):
        # Deterministic original text: same date => same fortune, next date => changes.
        a=FORTUNE_SENTENCES[(seed+idx*3)%len(FORTUNE_SENTENCES)]
        b=FORTUNE_SENTENCES[(seed+idx*3+5)%len(FORTUNE_SENTENCES)]
        c=FORTUNE_SENTENCES[(seed+idx*3+9)%len(FORTUNE_SENTENCES)]
        score=34+((seed*7+idx*13)%61)
        money=max(30,min(95,score+(((idx+1)*7)%11-5)))
        health=max(30,min(95,score+(((idx+2)*5)%11-5)))
        love=max(30,min(95,score+(((idx+3)*3)%11-5)))
        yr=", ".join(f"{y:02d}" if y<10 else str(y) for y in years[:2])+"년생"
        others=", ".join(f"{y:02d}" if y<10 else str(y) for y in years[2:])
        lines += [f"〈{name}〉","",f"{yr} {a} {others}년생 {b} {c}","",
                  f"운세지수 {score}%. 금전 {money} 건강 {health} 애정 {love}",""]
    return "\n".join(lines).strip()

def google_headlines(limit=11):
    url="https://news.google.com/rss?"+urllib.parse.urlencode({"hl":"ko","gl":"KR","ceid":"KR:ko"})
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=25) as r: raw=r.read()
    root=ET.fromstring(raw)
    out=[]
    for node in root.findall(".//item"):
        title=(node.findtext("title") or "").strip()
        # Google News often appends publisher name after " - "
        title=re.sub(r"\s+-\s+[^-]+$","",title).strip()
        if title and title not in out: out.append(title)
        if len(out)>=limit: break
    return out

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>","",s or "")).strip()

def naver_news(query, limit=10):
    cid=os.getenv("NAVER_CLIENT_ID","").strip()
    secret=os.getenv("NAVER_CLIENT_SECRET","").strip()
    if not cid or not secret:
        return [{"title":"네이버 API 키를 등록하면 오늘의 부동산 주요뉴스가 자동으로 표시됩니다.","url":""}]
    q=urllib.parse.urlencode({"query":query,"display":50,"start":1,"sort":"date","format":"json"})
    url="https://naverapihub.apigw.ntruss.com/search/v1/news?"+q
    headers={
        "User-Agent":"Mozilla/5.0",
        "X-NCP-APIGW-API-KEY-ID":cid,
        "X-NCP-APIGW-API-KEY":secret,
    }
    j=get_json(url,headers=headers)
    out=[]; seen=set()
    for it in j.get("items",[]):
        title=strip_tags(it.get("title",""))
        link=(it.get("link") or it.get("originallink") or "").strip()
        key=re.sub(r"\s+","",title)
        if not title or key in seen: continue
        seen.add(key)
        out.append({"title":title,"url":link})
        if len(out)>=limit: break
    return out

def positive_comment(now, weather):
    weekday="월화수목금토일"[now.weekday()]
    phrases={
        "월":"새로운 한 주가 시작됐습니다. 큰 결정보다 오늘 할 수 있는 한 가지를 끝내는 것부터 시작해보세요.",
        "화":"어제보다 한 걸음만 더 나아가도 충분합니다. 꾸준함이 결국 가장 큰 차이를 만듭니다.",
        "수":"한 주의 가운데입니다. 지금까지 잘 버텨온 만큼 오늘은 속도보다 방향을 점검해보세요.",
        "목":"조금만 더 가면 한 주의 결실이 보입니다. 오늘의 작은 실행이 내일의 여유를 만듭니다.",
        "금":"한 주 동안 쌓아온 노력이 빛을 보는 날입니다. 잘한 것은 인정하고 부족한 것은 다음 기회로 남겨두세요.",
        "토":"잠시 속도를 늦추고 자신을 채우는 것도 앞으로 나아가는 과정입니다. 좋은 사람과 좋은 시간을 보내세요.",
        "일":"새로운 한 주를 준비하는 날입니다. 걱정보다 기대할 일을 하나 만들어두면 내일이 훨씬 가벼워집니다."
    }
    return f"💛 오늘의 긍정코멘트\n\n{phrases[weekday]}"

now=datetime.now(KST)
weekday="월화수목금토일"[now.weekday()]
wtext=weather_text(now)
headlines=google_headlines(11)
realestate=naver_news("부동산 OR 아파트 OR 주택 OR 분양 OR 청약",10)

payload={
    "date_label":f"{now:%Y년 %-m월 %-d일} {weekday}요일",
    "updated_at":now.strftime("%H:%M"),
    "sections":[
        {"title":"1. 🔮 오늘의 운세","text":fortune_text(now)},
        {"title":"2. 🌤️ 오늘의 날씨","text":wtext},
        {"title":"3. 💛 아침 헤드라인 뉴스","items":[{"title":x} for x in headlines]},
        {"title":"4. 🏠 부동산 주요뉴스","items":realestate},
        {"title":"5. 🌱 오늘의 긍정코멘트 한마디","text":positive_comment(now,wtext)}
    ]
}
DATA.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print("updated",DATA)
