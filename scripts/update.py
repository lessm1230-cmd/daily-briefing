from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
import json, os, re, html, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
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

def get_json(url, headers=None, retries=3, timeout=12):
    req = urllib.request.Request(url, headers=headers or {"User-Agent":"Mozilla/5.0"})
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    raise last_err

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
    lines = ["❒ 지역별 날씨전망 ❒", ""]
    ok_count = 0

    for name,(lat,lon) in CITIES.items():
        q = urllib.parse.urlencode({
            "latitude":lat,"longitude":lon,
            "hourly":"weather_code",
            "daily":"temperature_2m_max,temperature_2m_min",
            "timezone":"Asia/Seoul","forecast_days":1
        })
        url = "https://api.open-meteo.com/v1/forecast?" + q

        try:
            j = get_json(url, retries=3, timeout=12)
            times = j["hourly"]["time"]
            codes = j["hourly"]["weather_code"]

            morning_key = now.strftime("%Y-%m-%d") + "T08:00"
            afternoon_key = now.strftime("%Y-%m-%d") + "T15:00"

            mcode = codes[times.index(morning_key)] if morning_key in times else codes[8]
            acode = codes[times.index(afternoon_key)] if afternoon_key in times else codes[15]

            lo = round(j["daily"]["temperature_2m_min"][0])
            hi = round(j["daily"]["temperature_2m_max"][0])

            lines.append(f"✫{name}({weather_emoji(mcode)})➠({weather_emoji(acode)})  {lo}℃ ~ {hi}℃")
            ok_count += 1

        except Exception as e:
            # 한 도시의 날씨 API가 잠시 실패해도 전체 브리핑 생성은 계속 진행
            print(f"WEATHER WARNING [{name}]: {e}")
            lines.append(f"✫{name} 날씨정보 일시 지연")

    if ok_count == 0:
        lines.append("")
        lines.append("※ 날씨 제공 서버 응답이 지연되고 있습니다. 다음 자동 업데이트에서 다시 시도합니다.")

    return "\n".join(lines)

def fortune_text(now):
    cal = KoreanLunarCalendar()
    cal.setSolarDate(now.year, now.month, now.day)
    gapja = cal.getGapJaString()
    day_ganji = ""
    m = re.search(r"([가-힣]{2})일", gapja)
    if m:
        day_ganji = m.group(1)

    lines=[f"[음력 {cal.lunarMonth}월 {cal.lunarDay}일] 일진: {day_ganji}",""]
    seed=now.year*10000+now.month*100+now.day

    for idx,(name,years) in enumerate(ZODIAC):
        a=FORTUNE_SENTENCES[(seed+idx*3)%len(FORTUNE_SENTENCES)]
        b=FORTUNE_SENTENCES[(seed+idx*3+5)%len(FORTUNE_SENTENCES)]
        c=FORTUNE_SENTENCES[(seed+idx*3+9)%len(FORTUNE_SENTENCES)]

        score=34+((seed*7+idx*13)%61)
        money=max(30,min(95,score+(((idx+1)*7)%11-5)))
        health=max(30,min(95,score+(((idx+2)*5)%11-5)))
        love=max(30,min(95,score+(((idx+3)*3)%11-5)))

        yr=", ".join(f"{y:02d}" if y<10 else str(y) for y in years[:2])+"년생"
        others=", ".join(f"{y:02d}" if y<10 else str(y) for y in years[2:])

        lines += [
            f"〈{name}〉","",
            f"{yr} {a} {others}년생 {b} {c}","",
            f"운세지수 {score}%. 금전 {money} 건강 {health} 애정 {love}",""
        ]
    return "\n".join(lines).strip()

def google_headlines(limit=11):
    try:
        url="https://news.google.com/rss?"+urllib.parse.urlencode({"hl":"ko","gl":"KR","ceid":"KR:ko"})
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=15) as r:
            raw=r.read()

        root=ET.fromstring(raw)
        out=[]
        for node in root.findall(".//item"):
            title=(node.findtext("title") or "").strip()
            title=re.sub(r"\s+-\s+[^-]+$","",title).strip()
            if title and title not in out:
                out.append(title)
            if len(out)>=limit:
                break
        return out
    except Exception as e:
        print("HEADLINE WARNING:", e)
        return ["헤드라인 뉴스 서버 응답이 지연되고 있습니다. 다음 자동 업데이트에서 다시 시도합니다."]

def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>","",s or "")).strip()

def naver_news(now, limit=10):
    cid=os.getenv("NAVER_CLIENT_ID","").strip()
    secret=os.getenv("NAVER_CLIENT_SECRET","").strip()

    if not cid or not secret:
        print("WARNING: NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 GitHub Secrets에서 전달되지 않았습니다.")
        return [{"title":"[설정 필요] GitHub Secrets에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 등록해주세요.","url":""}]

    headers={
        "User-Agent":"Mozilla/5.0",
        "X-NCP-APIGW-API-KEY-ID":cid,
        "X-NCP-APIGW-API-KEY":secret,
    }

    # 부동산 핵심 검색어
    queries=[
        "부동산",
        "아파트",
        "집값",
        "주택 공급",
        "청약 분양",
        "전세 월세",
        "재건축 재개발"
    ]

    # 제목에 아래 키워드가 하나 이상 있어야 최종 노출
    include_keywords=[
        "부동산","아파트","주택","집값","전세","월세","청약","분양",
        "재건축","재개발","토허","토지거래허가","매매","임대","임차",
        "공급","입주","미분양","주담대","주택담보","분양가","전셋값",
        "월셋값","공시가격","정비사업","조합원","입주권","분양권",
        "LH","한국토지주택공사","국토부","국토교통부","부동산원",
        "용적률","건폐율","재정비","신도시","택지","오피스텔"
    ]

    # 부동산 키워드가 우연히 섞여도 아래 유형이면 제외
    exclude_keywords=[
        "연예","가수","배우","아이돌","TSMC","반도체","의사","병원",
        "살인","사망","화재","대통령 지지율","정당","국민의힘","민주당",
        "야구","축구","농구","코인","비트코인","증시","주식"
    ]

    run_now = now.astimezone(KST)
    window_start = (run_now - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    window_end = run_now

    collected=[]
    seen=set()

    def is_realestate_title(title):
        compact = re.sub(r"\s+","",title)
        if any(bad in compact for bad in exclude_keywords):
            return False
        return any(good in compact for good in include_keywords)

    for query in queries:
        try:
            q=urllib.parse.urlencode({
                "query":query,
                "display":100,
                "start":1,
                "sort":"date",
                "format":"json"
            })
            url="https://naverapihub.apigw.ntruss.com/search/v1/news?"+q
            j=get_json(url,headers=headers,retries=2,timeout=15)

            for it in j.get("items",[]):
                title=strip_tags(it.get("title",""))
                link=(it.get("link") or "").strip()
                pub_raw=(it.get("pubDate") or "").strip()

                # 네이버 뉴스 내부 기사만
                if not (
                    "n.news.naver.com/" in link
                    or "news.naver.com/" in link
                    or "m.news.naver.com/" in link
                ):
                    continue

                # 제목 자체가 부동산 기사인지 한 번 더 엄격하게 검사
                if not is_realestate_title(title):
                    continue

                # 전날 18:00 ~ 현재 실행시각 사이 기사만
                try:
                    pub_dt=parsedate_to_datetime(pub_raw)
                    if pub_dt.tzinfo is None:
                        pub_dt=pub_dt.replace(tzinfo=KST)
                    pub_kst=pub_dt.astimezone(KST)
                except Exception:
                    continue

                if not (window_start <= pub_kst <= window_end):
                    continue

                key=re.sub(r"[^0-9A-Za-z가-힣]","",title)
                if not title or key in seen:
                    continue

                seen.add(key)
                collected.append({
                    "title":title,
                    "url":link,
                    "_published":pub_kst
                })

        except Exception as e:
            print(f"NAVER NEWS WARNING [{query}]: {e}")

    collected.sort(key=lambda x:x["_published"],reverse=True)
    out=[{"title":x["title"],"url":x["url"]} for x in collected[:limit]]

    if not out:
        return [{
            "title":"전날 오후 6시 이후의 네이버 부동산 주요뉴스가 아직 없습니다. 다음 자동 업데이트 때 다시 확인해주세요.",
            "url":""
        }]

    return out

def positive_comment(now):
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
    return phrases[weekday]

now=datetime.now(KST)
weekday="월화수목금토일"[now.weekday()]

wtext=weather_text(now)
headlines=google_headlines(11)
realestate=naver_news(now,10)

payload={
    "date_label":f"{now:%Y년 %-m월 %-d일} {weekday}요일",
    "updated_at":now.strftime("%H:%M"),
    "sections":[
        {"title":f"오늘의 운세, {now.month}월 {now.day}일","text":fortune_text(now)},
        {"title":f"{now:%Y년 %-m월 %-d일} {weekday}요일","text":wtext},
        {"title":"💛 아침 헤드라인 뉴스","number_items":True,
         "items":[{"title":x} for x in headlines]},
        {"title":f"{str(now.year)[2:]}년 {now.month}월 {now.day}일 {weekday}요일 부동산 주요뉴스",
         "number_items":False,"items":realestate},
        {"title":"🌱 오늘의 긍정코멘트 한마디","text":positive_comment(now)}
    ]
}

DATA.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
print("updated",DATA)
