@echo off
setlocal
chcp 65001 >nul
python "%~dp0terminal_app.py" %*
