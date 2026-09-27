@echo off
chcp 65001 >nul
setlocal
title 家音 · 一键启动

echo ========================================
echo   家音 Jiayin · 一键启动
echo ========================================
echo.

REM 后端
echo [1/2] 启动后端 (uvicorn :8000)...
start "家音-后端" cmd /k "cd /d %~dp0backend && .\.venv\Scripts\python.exe -m uvicorn main:app --port 8000"

REM 等待后端起来
timeout /t 2 /nobreak >nul

REM 前端（系统无 Node，用便携版；若已装 Node 可去掉前面的 PATH 注入）
echo [2/2] 启动前端 (vite :5173)...
start "家音-前端" cmd /k "set PATH=C:\Users\潘亦然\CodeBuddy\20260922211024\node-v20.18.0-win-x64;%PATH% && cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   后端：http://localhost:8000
echo   前端：http://localhost:5173
echo   接口文档：http://localhost:8000/docs
echo.
echo   关闭两个黑色窗口即可停止服务
echo ========================================
echo.
pause