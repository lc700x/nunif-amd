@echo off
cls
Set "VIRTUAL_ENV=venv"
echo - Make sure you have moved ZLUDA folder to current directory. Patching ZLUDA...
copy zluda\cublas.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\cublas64_11.dll /y >NUL
copy zluda\cusparse.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\cusparse64_11.dll /y >NUL
copy zluda\nvrtc.dll %VIRTUAL_ENV%\Lib\site-packages\torch\lib\nvrtc64_112_0.dll /y >NUL
echo - ZLUDA is patched.
echo.
echo You can now use the iw3 gui and cli with gpu acceleration with amd gpu's. 
echo Run iw3z.bat to start iw3 with amd gpu support. 
echo.
echo ******** The first time you select a model and generate, (only a new type of model) it would seem like your computer is doing nothing, 
echo ******** that's normal , zluda is creating a database for future use. That only happens once for every new type of model.
echo ******** you will see a few "compilation in progress..." message, wait for a while.
pause
