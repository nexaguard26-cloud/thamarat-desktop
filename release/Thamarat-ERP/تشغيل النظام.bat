@echo off
chcp 65001 >nul
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║        Thamarat ERP - نظام المحاسبة             ║
echo  ║        Humanitarian Accounting System            ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: Check if backend is running
netstat -ano | findstr ":5000" >nul
if %errorlevel%==0 (
    echo [!] Backend already running on port 5000
    goto :openBrowser
)

echo [*] Starting Thamarat Backend Server...
start "Thamarat Backend" /min "ThamaratBackend.exe"

:: Wait for backend to start
echo [*] Waiting for server to start...
timeout /t 3 /nobreak >nul

:openBrowser
echo [*] Opening Thamarat ERP...
start "" "frontend\index.html"

echo.
echo ✅ Thamarat ERP is now running!
echo    - Backend: http://localhost:5000
echo    - Frontend: frontend\index.html
echo.
echo بيانات الدخول:
echo    Email: admin@thamarat.local
echo    Password: Admin@123
echo.
pause
