@echo off
chcp 65001 >nul
setlocal
title 家音 · 应急公网链接（cloudflared 临时隧道）

echo ========================================
echo   家音 · 应急公网链接（cloudflared）
echo ========================================
echo.

REM ---------- 检查 cloudflared ----------
set CLOUDFLARED=cloudflared-windows-amd64.exe
if not exist "%~dp0%CLOUDFLARED%" (
    echo [1/4] 下载 cloudflared ...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%~dp0%CLOUDFLARED%' -UseBasicParsing"
    if not exist "%~dp0%CLOUDFLARED%" (
        echo [ERROR] 下载失败，请检查网络
        pause
        exit /b 1
    )
)

REM ---------- 检查服务 ----------
echo [2/4] 检查后端 :8000 ...
powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 3).StatusCode } catch { Write-Host '未启动' ; exit 1 }"
if errorlevel 1 (
    echo [ERROR] 后端未启动，请先双击 start.bat
    pause
    exit /b 1
)

echo [3/4] 检查前端 :4173 ...
powershell -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:4173/' -UseBasicParsing -TimeoutSec 3).StatusCode } catch { Write-Host '未启动' ; exit 1 }"
if errorlevel 1 (
    echo [ERROR] 前端未启动，请先双击 start.bat
    pause
    exit /b 1
)

echo [4/4] 启动公网隧道 ...
echo.
echo ========================================
echo   即将输出公网链接，找类似这一行：
echo   https://xxxx-xxxx.trycloudflare.com
echo.
echo   复制这个链接发给评委就行
echo   关掉本窗口即断开
echo ========================================
echo.

"%~dp0%CLOUDFLARED%" tunnel --url http://127.0.0.1:4173

pause