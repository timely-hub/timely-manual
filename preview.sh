#!/usr/bin/env bash
# preview.sh — 로컬에서 사이트를 띄우고 파일 저장 시 즉시 반영합니다.
#
# 사용법:
#   ./preview.sh
#
# 처음 실행하면 자동으로 가상환경(.venv)을 만들고 의존성을 설치한 뒤
# http://127.0.0.1:8000 에 서버를 띄웁니다.
# Ctrl+C 로 종료합니다.

set -euo pipefail
cd "$(dirname "$0")"

# 1) 첫 실행이면 .venv 만들고 의존성 설치
if [ ! -x .venv/bin/mkdocs ]; then
  echo "📦 첫 실행 — 가상환경(.venv) 만들고 의존성 설치 중..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip --quiet
  .venv/bin/pip install -r requirements.txt --quiet
fi

# 2) 포트 8000이 이미 쓰이고 있으면 다른 포트로 자동 fallback
PORT="${MKDOCS_PORT:-8000}"
while lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do
  PORT=$((PORT + 1))
done

echo ""
echo "🚀  http://127.0.0.1:${PORT} 에서 미리보기 시작합니다."
echo "    파일을 저장하면 브라우저에서 자동으로 새로고침돼요."
echo "    종료: Ctrl+C"
echo ""

exec .venv/bin/mkdocs serve --dev-addr="127.0.0.1:${PORT}"
