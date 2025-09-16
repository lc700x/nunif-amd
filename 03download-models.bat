@echo off
cls
Set "VIRTUAL_ENV=venv"
echo - Virtual enviroment activation
Call "%VIRTUAL_ENV%\Scripts\activate.bat"
echo - Downloading models
echo.
python -m iw3.download_models
echo.
echo - Models downladed.
pause