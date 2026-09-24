복구팩입니다.

기존 루트의 index.html, data.json, scripts/update.py는 건드리지 마세요.

필요한 파일:
.github/workflows/daily.yml
scripts/update_subscription.py
subscription/index.html
subscription/data.json

추가 확인:
GitHub Settings → Secrets and variables → Actions 에 아래 3개가 있어야 합니다.
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
DATA_GO_KR_API_KEY
