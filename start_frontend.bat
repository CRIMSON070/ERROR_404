@echo off
echo ====================================
echo IPL Auction Platform - Frontend UI
echo ====================================
echo.
echo Starting Streamlit frontend on port 8501...
echo.
cd /d "%~dp0"
python -m streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 8501
pause
