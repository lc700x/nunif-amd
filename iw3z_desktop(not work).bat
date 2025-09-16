@echo off
call .\venv\Scripts\activate
.\zluda\zluda.exe -- python -m iw3.desktop.gui
exit /b 0
