@echo off
echo ====================================
echo IPL Auction Platform - Backend Server
echo ====================================
echo.
echo Starting FastAPI backend on port 8000...
echo.
cd /d "%~dp0"
python run_backend.py
pause
