@echo off
cls
echo --- IW3 Installer for AMD GPU's on Windows (With ZLUDA)---
echo.
echo - Make sure you have installed HIP and copied your libraries (if you have and older gpu) before installing this.
echo.
echo - Setting up the virtual enviroment
Set "VIRTUAL_ENV=venv"
If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" (
    python.exe -m venv %VIRTUAL_ENV%
)
If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" Exit /B 1
echo - Virtual enviroment activation
Call "%VIRTUAL_ENV%\Scripts\activate.bat"
echo - Updating the pip package
python.exe -m pip install --upgrade pip --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
echo.
echo - Installing torch for AMD GPUs (Using latest torch 2.7.0)
pip install numpy==2.1.2 --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
pip install sympy==1.13.3 --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu118  --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
echo.
echo - Installing necessary packages
pip install -r requirements.txt --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
pip install -r requirements-gui.txt --trusted-host http://mirrors.aliyun.com/pypi/simple/ --no-cache
echo.
echo Python enviroment deployed. 
