@echo off
title S1M0N Launcher

echo ========================================
echo   CONTENT ROBOT v8.3 - GOOGLE ECOSYSTEM
echo ========================================
echo.

cd /d "%~dp0"

REM --- CHECK PYTHON ---
python --version >nul 2>&1
if errorlevel 1 goto NoPython

REM --- CHECK VENV ---
if exist venv\Scripts\activate.bat goto ActivateVenv
goto StartEngine

:ActivateVenv
echo [INFO] Ativando ambiente virtual (venv)...
call venv\Scripts\activate.bat
goto StartEngine

:StartEngine
echo.
echo [1/3] Iniciando Engine (Main Loop)...
start "S1M0N Engine" cmd /k "python main.py"

REM --- WAIT ---
timeout /t 5 /nobreak > nul

REM --- START DASHBOARD ---
echo [2/3] Iniciando Dashboard Web...
start "S1M0N Dashboard" cmd /k "python dashboard_launcher.py"

echo.
echo ========================================
echo   SISTEMA INICIADO
echo ========================================
echo.
echo   - Dashboard: http://localhost:5000
echo.
echo   Pressione qualquer tecla para encerrar TUDO...
pause > nul

REM --- SHUTDOWN ---
taskkill /FI "WINDOWTITLE eq S1M0N Engine" /F
taskkill /FI "WINDOWTITLE eq S1M0N Dashboard" /F
goto End

:NoPython
echo.
echo [ERROR] Python nao encontrado. Instale o Python 3.10+ e adicione ao PATH.
pause
goto End

:End
echo [OFF] Encerrado.
timeout /t 3 > nul
