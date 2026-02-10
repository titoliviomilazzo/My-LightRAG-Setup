@echo off
REM Simple .env updater (Windows CMD)
REM Usage: set_env_value.bat KEY VALUE
if "%~1"=="" (
  echo Usage: %~nx0 KEY VALUE
  exit /b 1
)
if "%~2"=="" (
  echo Usage: %~nx0 KEY VALUE
  exit /b 1
)
set KEY=%~1
set VALUE=%~2
cd /d %~dp0\..
if not exist .env (
  echo .env not found
  exit /b 1
)
copy .env .env.bak.%DATE%_%TIME% >nul
setlocal enabledelayedexpansion
set FOUND=0
for /f "usebackq delims=" %%L in (".env") do (
  set "line=%%L"
  for /f "tokens=1* delims==" %%A in ("!line!") do (
    if /i "%%A"=="%KEY%" (
      echo %KEY%=%VALUE%>>.env.tmp
      set FOUND=1
    ) else (
      echo %%A=%%B>>.env.tmp
    )
  )
)
if "%FOUND%"=="0" echo %KEY%=%VALUE%>>.env.tmp
move /y .env.tmp .env >nul
endlocal
echo .env updated. Restart server to apply changes.
