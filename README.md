# 오늘의 청약소식 추가 페이지

기존 브리핑은 그대로 두고 같은 저장소에 `/subscription/` 페이지를 추가합니다.

예:
`https://아이디.github.io/daily-briefing/subscription/`

## 표시 기준
- 일반 APT 청약
- APT 무순위/잔여세대
- 현재 접수중
- 7일 이내 접수예정
- 오늘 당첨자 발표
- 마감일 빠른 순 정렬
- D-DAY / D-1 빨간 배지
- 접수중 / 마감임박 / 오늘발표 카운트

## 필요한 API 키
공공데이터포털에서 `한국부동산원_청약홈 분양정보 조회 서비스` 활용신청 후 서비스키를 발급받습니다.

GitHub:
Settings → Secrets and variables → Actions → New repository secret

Name:
`DATA_GO_KR_API_KEY`

Secret:
공공데이터포털 서비스키

## 기존 저장소에 추가
1. `subscription` 폴더 전체
2. `scripts/update_subscription.py`
3. `.github/workflows/daily.yml`을 이 패키지 버전으로 교체
4. GitHub Secret `DATA_GO_KR_API_KEY` 등록
5. Actions → Daily Briefing Update & Deploy → Run workflow

기존 `index.html`과 기존 `scripts/update.py`는 그대로 둡니다.
