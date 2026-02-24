@echo off
REM 実行用バッチファイル
REM Created: 2026-02-17

cd /d %~dp0
call .venv\Scripts\activate.bat
python main.py %*
pause
