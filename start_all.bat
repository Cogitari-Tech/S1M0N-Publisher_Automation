@echo off
echo ========================================
echo   CONTENT ROBOT v7.0 - GOOGLE EDITION
echo ========================================
echo.

cd /d "%~dp0"

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo [1/3] Iniciando Engine (Main Loop)......
start "Content Engine v7" cmd /k python main.py

timeout /t 3 /nobreak > nul

echo [2/3] Iniciando Dashboard Web...........
start "Dashboard v7" cmd /k python dashboard_launcher.py

timeout /t 3 /nobreak > nul

echo [3/3] Iniciando Sistema de Aprovacao....
REM Mantivemos o approval_system.py na raiz por compatibilidade
start "Approval System" cmd /k python approval_system.py

echo.
echo ========================================
echo   TODOS OS SISTEMAS ONLINE!
echo ========================================
echo.
echo   - Dashboard: http://localhost:5000
echo   - Aprovacao: http://localhost:5001
echo.
echo   Pressione qualquer tecla para encerrar todos os processos...
pause > nul

taskkill /FI "WINDOWTITLE eq Content Engine v7" /F
taskkill /FI "WINDOWTITLE eq Dashboard v7" /F
taskkill /FI "WINDOWTITLE eq Approval System" /F