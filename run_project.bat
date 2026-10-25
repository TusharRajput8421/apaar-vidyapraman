@echo off
echo ========================================================
echo   Starting VidyaPraman (AICTE APAAR Platform - SIH 26263)
echo ========================================================
echo.
start "" http://localhost:8000
start "" "presentation\VidyaPraman_SIH_Deck.html"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
