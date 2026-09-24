# 오늘의 브리핑 v3

순서:
1. 오늘의 운세
2. 오늘의 날씨
3. 아침 헤드라인 뉴스
4. 부동산 주요뉴스
5. 오늘의 긍정코멘트 한마디

각 섹션 오른쪽에 복사 버튼이 있고, 상단에는 전체복사 버튼이 있습니다.

## 중요
- 운세: 다른 매체 문구를 복사하지 않고 매일 날짜별로 새로 생성되는 원문형 운세입니다.
- 날씨: Open-Meteo 데이터를 이용해 오전 8시 → 오후 3시 날씨 아이콘과 일 최저/최고기온을 표시합니다.
- 아침 헤드라인: Google News 한국 RSS의 최신 제목만 표시합니다.
- 부동산 주요뉴스: NAVER API HUB 뉴스 검색 API를 사용합니다.
- 긍정코멘트: 요일에 맞춰 매일 바뀝니다.

## GitHub에서 필요한 설정

### 1) Pages
Repository → Settings → Pages → Source = GitHub Actions

### 2) 네이버 부동산 뉴스용 API 키
2026년 현재 신규 검색 API는 NAVER Cloud Platform의 NAVER API HUB에서 발급합니다.

발급 후 GitHub Repository에서:
Settings → Secrets and variables → Actions → New repository secret

두 개를 등록:
- Name: NAVER_CLIENT_ID
- Name: NAVER_CLIENT_SECRET

값에는 NAVER API HUB에서 발급받은 Client ID / Client Secret을 각각 입력합니다.

### 3) 수동 테스트
Actions → Daily Briefing Update & Deploy → Run workflow

초록색 체크가 뜨면 배포 성공입니다.

### 4) 자동 실행
매일 한국시간 오전 7시 5분경 자동 실행됩니다.


## v4 변경사항
- 섹션 제목 앞의 1., 2., 3., 4., 5. 제거
- 아침 헤드라인만 1~11 번호 유지
- 부동산 뉴스는 번호 없이 `제목 + 링크`로 표시/복사
- NAVER 비밀키가 전달되지 않으면 Actions 로그에 경고 표시

## 부동산 뉴스가 안 나오면
GitHub 저장소:
Settings → Secrets and variables → Actions → Repository secrets

정확히 아래 두 이름이 있어야 합니다.
- NAVER_CLIENT_ID
- NAVER_CLIENT_SECRET

등록 후 Actions에서 다시 `Run workflow`를 실행하세요.
