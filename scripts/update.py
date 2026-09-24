from pathlib import Path
from datetime import datetime
import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data.json"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def weather_text():
    # 키 없이 쓸 수 있는 Open-Meteo 예시.
    # 원하는 도시를 추가/삭제하면 됩니다.
    cities = {
        "서울": (37.5665, 126.9780),
        "부산": (35.1796, 129.0756),
        "대구": (35.8714, 128.6014),
        "대전": (36.3504, 127.3845),
        "광주": (35.1595, 126.8526),
    }
    lines=[]
    for name,(lat,lon) in cities.items():
        q=urllib.parse.urlencode({
            "latitude":lat, "longitude":lon,
            "daily":"temperature_2m_max,temperature_2m_min,weather_code",
            "timezone":"Asia/Seoul", "forecast_days":1
        })
        j=get_json("https://api.open-meteo.com/v1/forecast?"+q)
        lo=round(j["daily"]["temperature_2m_min"][0])
        hi=round(j["daily"]["temperature_2m_max"][0])
        lines.append(f"{name} {lo}℃ ~ {hi}℃")
    return "\n".join(lines)

def google_news_items(query="부동산"):
    # Google News RSS 기반 예시. 별도 API 키 없이 동작.
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({
        "q":query, "hl":"ko", "gl":"KR", "ceid":"KR:ko"
    })
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw=r.read()
    root=ET.fromstring(raw)
    items=[]
    for node in root.findall(".//item")[:8]:
        title=(node.findtext("title") or "").strip()
        link=(node.findtext("link") or "").strip()
        pub=(node.findtext("pubDate") or "").strip()
        items.append({"title":title, "summary":"", "meta":pub, "url":link})
    return items

now=datetime.now()
weekday="월화수목금토일"[now.weekday()]
payload={
    "date_label": f"{now:%Y년 %m월 %d일} {weekday}요일",
    "updated_at": now.strftime("%H:%M"),
    "sections":[
        {"title":"1. ☀️ 오늘의 날씨", "text":weather_text()},
        {"title":"2. 📰 오늘의 부동산 뉴스", "items":google_news_items("부동산 OR 분양 OR 청약")},
        {"title":"3. 🏠 청약·분양 소식",
         "text":"이 영역은 청약홈/공공데이터포털 API를 연결하면 자동화할 수 있습니다. API 키가 필요한 경우 GitHub Secrets에 넣어 사용하세요."},
        {"title":"4. 📌 방장용 한줄 브리핑",
         "text":"오늘의 핵심 뉴스와 시장 흐름을 오픈채팅용 문장으로 자동 생성하도록 확장할 수 있습니다."}
    ]
}
DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("updated", DATA)
