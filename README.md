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


## v5 변경사항
- 부동산 뉴스는 `n.news.naver.com`, `news.naver.com`, `m.news.naver.com` 주소만 표시
- 외부 언론사 직접 링크(breaknews 등)는 제외
- 최대 100개 검색결과에서 네이버 뉴스 내부기사 10개를 추림
- 긍정코멘트 본문에 중복으로 나오던 `💛 오늘의 긍정코멘트` 문구 제거


## v6 변경사항
- 부동산 뉴스 제목을 자동으로 `26년 9월 24일 목요일 부동산 주요뉴스` 형식으로 표시
- NAVER API의 `pubDate`를 한국시간으로 변환
- 오늘 날짜와 일치하는 기사만 표시
- `부동산 / 아파트 / 주택 공급 / 청약 분양 / 재건축 재개발`을 각각 검색해 당일 기사 확보
- 중복 제거 후 최신 발행 시각 순으로 최대 10개 표시
- 네이버 뉴스 내부 링크만 유지


## v7 변경사항
- 운세의 `🔮 오늘의 운세` 중복 제목 제거
- 날씨의 `🌤️ 오늘의 날씨` 중복 제목 제거
- 운세는 `오늘의 운세, 9월 24일`로 바로 복사
- 날씨는 `2026년 9월 24일 목요일`로 바로 복사
- 각 섹션 펼치기/접기 기능 추가
- 기본 화면은 모두 접힌 컴팩트 모드
- 접힌 상태에서도 각 항목 `복사` 가능
- 상단 `모두 접기 / 모두 펼치기 / 전체복사` 버튼 추가
- 모두 접으면 5개 항목을 한 화면에서 빠르게 복사 가능
