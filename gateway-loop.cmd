@echo off
:loop
echo [%date% %time%] Starting Hermes Gateway...
cd /d "C:\AI\Agents\hermes-agent-clean"
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" -m gateway.run
echo [%date% %time%] Gateway exited with code %errorlevel%. Restarting in 10s...
timeout /t 10 /noq
goto loop
