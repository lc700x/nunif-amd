@echo off
cls
echo --- IW3 Installer for AMD GPU's on Windows (With ZLUDA)---
echo.
echo - Make sure you have installed HIP 6.2.4 and copied your libraries (if you have and older gpu) before installing this.
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
python.exe -m pip install --upgrade pip --quiet
echo.
echo - Installing necessary packages
pip install -r requirements.txt --quiet
pip install -r requirements-gui.txt --quiet
echo.
echo - Installing torch for AMD GPUs (Using latest torch 2.7.0)
pip install torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu118 --quiet
echo.
echo - Downloading models
echo.
python -m iw3.download_models
echo.
echo - Patching ZLUDA (Zluda 3.9.5 for HIP SDK 6.2.4)
%SystemRoot%\system32\curl -sL --ssl-no-revoke https://github.com/lshqqytiger/ZLUDA/releases/download/rel.5e717459179dc272b7d7d23391f0fad66c7459cf/ZLUDA-windows-rocm6-amd64.zip > zluda.zip
%SystemRoot%\system32\tar -xf zluda.zip
del zluda.zip
copy zluda\cublas.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\cublas64_11.dll /y >NUL
copy zluda\cusparse.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\cusparse64_11.dll /y >NUL
copy zluda\nvrtc.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\nvrtc64_112_0.dll /y >NUL
echo - ZLUDA is patched. (Zluda 3.9.5 for HIP 6.2.4)
echo.
echo You can now use the iw3 gui & cli with gpu acceleration with amd gpu's. 
echo Run iw3z.bat to start iw3 with amd gpu support. 
echo.
echo ******** The first time you select a model and generate, (only a new type of model) it would seem like your computer is doing nothing, 
echo ******** that's normal , zluda is creating a database for future use. That only happens once for every new type of model.
echo ******** you will see a few "compilation in progress..." message, wait for a while.
pause

