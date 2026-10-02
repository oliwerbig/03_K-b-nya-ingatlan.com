@echo off
cd /d "%~dp0"
echo Indul a JupyterLab...
".venv\Scripts\python.exe" -m jupyterlab
pause