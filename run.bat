@echo off
cd /d %~dp0
start cmd /k "python run_ngrok.py"
timeout /t 5 >nul
start cmd /k "streamlit run app.py"
pause