@echo off
title LifeLink Launcher
echo ========================================================
echo           Starting LifeLink Platform...
echo ========================================================
echo.

REM Start FastAPI Backend
echo [1/2] Starting Backend API on http://localhost:8000 ...
start "LifeLink Backend (FastAPI)" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

REM Start Frontend HTTP Server
echo [2/2] Starting Frontend Server on http://localhost:5500 ...
start "LifeLink Frontend (HTTP Server)" cmd /k "cd /d %~dp0frontend && python -m http.server 5500"

timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:5500

echo.
echo ========================================================
echo LifeLink started successfully!
echo - Frontend:      http://localhost:5500
echo - Backend Docs:  http://localhost:8000/docs
echo - API Base:      http://localhost:8000/api
echo ========================================================
pause
