@echo off
cd /d "%~dp0"
echo Indul a JupyterLab...
call ".venv\Scripts\activate.bat"
jupyter lab
pause