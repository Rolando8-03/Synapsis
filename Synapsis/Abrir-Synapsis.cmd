@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto check
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m venv .venv
if errorlevel 1 goto fail
goto check

:usepython
python -m venv .venv
if errorlevel 1 goto fail

:check
".venv\Scripts\python.exe" -c "import sympy, mpmath; from PySide6.QtWebEngineWidgets import QWebEngineView" >nul 2>nul
if not errorlevel 1 goto launch
echo Instalando los componentes de escritorio de Synapsis. Este paso requiere internet.
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto fail

:launch
".venv\Scripts\python.exe" abrir.py
if errorlevel 1 goto fail
exit /b 0

:fail
echo No se pudo iniciar Synapsis. Verifica que Python 3.10 o posterior este instalado.
pause
exit /b 1
