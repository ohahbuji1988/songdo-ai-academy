@echo off
chcp 65001 >nul
title Songdo AI Academy Server
echo ========================================================
echo   [Songdo AI Academy] Local Server & Dashboard Launcher
echo ========================================================
echo.
echo [1/2] Starting Python server on port 3000...
start /b python server.py
timeout /t 2 >nul
echo [2/2] Opening Dashboard in your browser...
start http://127.0.0.1:3000/
echo.
echo ========================================================
echo   * Public Live:  https://songdo-ai.pages.dev/
echo   * Local Portal: http://127.0.0.1:3000/
echo   * Landing:      http://127.0.0.1:3000/landing.html
echo   * Classroom:    http://127.0.0.1:3000/courseware/lessons.html
echo ========================================================
echo.
echo Press Ctrl+C or close this window to stop the server.
pause
