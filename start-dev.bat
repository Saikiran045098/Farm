@echo off
echo ===================================================
echo Starting FarmBuddy Fullstack Environment
echo Frontend: Next.js (http://localhost:3000)
echo Backend:  Python Django (http://127.0.0.1:8000)
echo ===================================================

start "FarmBuddy Backend (Django)" cmd /k "cd /d %~dp0backend && python manage.py migrate && python manage.py runserver 8000"
start "FarmBuddy Frontend (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Both servers are starting up in new windows!
pause
