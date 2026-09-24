# 오늘의 브리핑 자동 업데이트 페이지 v2

이 버전은 GitHub Actions가 매일 최신 데이터를 만든 뒤 GitHub Pages에 직접 배포합니다.

## 처음 설치
1. GitHub에서 새 PUBLIC 저장소를 만듭니다.
2. 이 폴더 안의 파일/폴더를 모두 업로드합니다.
3. 저장소 Settings → Pages → Build and deployment → Source에서 `GitHub Actions`를 선택합니다.
4. Actions 탭 → `Daily Briefing Update & Deploy` → `Run workflow`로 최초 실행합니다.
5. 실행이 초록색 체크가 되면 Settings → Pages에 공개 주소가 표시됩니다.

## 자동 실행
매일 한국시간 약 07:05에 자동 실행되도록 설정되어 있습니다.

## 파일
- index.html: 웹 화면 + 복사 버튼
- data.json: 예시 데이터(배포 때 최신 데이터로 다시 생성)
- scripts/update.py: 날씨/뉴스 수집
- .github/workflows/daily.yml: 매일 자동 실행 + Pages 배포

## 참고
GitHub Actions 예약 실행은 정확히 초 단위 보장되는 알람이 아니므로 트래픽 상황에 따라 몇 분 지연될 수 있습니다.
