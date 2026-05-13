@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

REM ============================================================================
REM  preview.bat — 윈도우에서 사용설명서를 로컬에 띄웁니다.
REM
REM  사용법:
REM    이 파일을 더블 클릭하거나, 명령 프롬프트에서
REM      preview.bat
REM    실행.
REM
REM  처음 실행 시 가상환경(.venv)을 자동으로 만들고 의존성을 설치합니다.
REM  이후에는 즉시 서버가 뜨고, 브라우저가 자동으로 열립니다.
REM  파일을 저장하면 브라우저가 자동으로 새로고침합니다.
REM  종료: 이 창에서 Ctrl+C 또는 창 닫기.
REM ============================================================================

REM 1) Python 확인
where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo [오류] Python을 찾을 수 없습니다.
  echo Claude Desktop을 재설치하거나 https://python.org 에서 Python 3.10 이상을 설치해주세요.
  echo.
  pause
  exit /b 1
)

REM 2) 첫 실행이면 .venv 만들고 의존성 설치
if not exist ".venv\Scripts\mkdocs.exe" (
  echo.
  echo [setup] 첫 실행 — 가상환경^(.venv^)을 만들고 의존성을 설치합니다.
  echo [setup] 잠시만 기다려주세요...
  echo.

  python -m venv .venv
  if errorlevel 1 goto :install_failed

  call .venv\Scripts\python.exe -m pip install --upgrade pip --quiet
  call .venv\Scripts\pip.exe install -r requirements.txt --quiet
  if errorlevel 1 goto :install_failed

  echo [setup] 설치 완료.
  echo.
)

REM 3) 비어 있는 포트 찾기 (기본 8000부터)
set PORT=8000
:findport
netstat -an | findstr "LISTENING" | findstr ":%PORT% " >nul 2>&1
if not errorlevel 1 (
  set /a PORT+=1
  goto findport
)

echo.
echo ============================================================
echo   미리보기:  http://127.0.0.1:%PORT%/timely-manual/
echo ============================================================
echo   파일을 저장하면 브라우저가 자동 새로고침됩니다.
echo   종료: 이 창에서 Ctrl+C 또는 창 닫기
echo ============================================================
echo.

REM 4) 2초 후 브라우저 자동 열기 (mkdocs가 바인딩될 시간 확보)
start "" /B cmd /C "timeout /t 2 /nobreak >nul & start http://127.0.0.1:%PORT%/timely-manual/"

REM 5) mkdocs serve 실행 (이 줄이 끝날 때까지 창 유지)
.venv\Scripts\mkdocs.exe serve --dev-addr=127.0.0.1:%PORT%
exit /b 0

:install_failed
echo.
echo [오류] 설치 중 문제가 발생했습니다.
echo 위쪽에 표시된 메시지를 확인해주세요.
echo.
pause
exit /b 1
