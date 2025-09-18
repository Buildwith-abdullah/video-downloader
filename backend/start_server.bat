@echo off
cd /d C:\Users\ABDULLAH\Desktop\video-downloader-starter\backend
call venv\Scripts\activate
REM open browser to frontend (optional)
start "" "C:\Users\ABDULLAH\Desktop\video-downloader-starter\frontend\index.html"
REM start uvicorn
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
