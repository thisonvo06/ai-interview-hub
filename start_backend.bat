@echo off
chcp 65001 >nul
title AI Interview Hub
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_app.ps1" -Mode Backend %*
if errorlevel 1 (
    echo.
    pause
    exit /b 1
)
