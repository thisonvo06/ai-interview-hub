@echo off
chcp 65001 >nul
title AI Interview Hub - Stop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_app.ps1" -Mode Stop
if errorlevel 1 (
    echo.
    pause
    exit /b 1
)
