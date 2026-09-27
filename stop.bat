@echo off
echo ========================================
echo   关闭家音后端与前端进程
echo ========================================
taskkill /FI "WINDOWTITLE eq 家音-后端*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq 家音-前端*" /T /F >nul 2>&1
echo 已尝试关闭。若端口仍占用，请手动结束 uvicorn / node 进程。
pause