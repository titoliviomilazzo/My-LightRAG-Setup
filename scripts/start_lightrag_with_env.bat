@echo off
REM Start script for LightRAG (Windows .bat)
REM - loads simple KEY=VALUE lines from .env into environment (naive parser)
REM - creates logs\ and writes stdout+stderr to logs\lightrag.log

cd /d %~dp0\..
if not exist logs mkdir logs
set LOGFILE=logs\lightrag.log
echo Loading .env
for /f "usebackq tokens=1* delims==" %%A in (".env") do (
    REM skip lines starting with # or empty
    if NOT "%%A"=="" (
        if NOT "%%A:~0,1%"=="#" (
            set "%%A=%%B"
        )
    )
)
echo Starting server, logging to %LOGFILE%
python -u -m lightrag.api.lightrag_server > %LOGFILE% 2>&1
echo Server exited. Tail of log:
type %LOGFILE%
