@echo off
REM ============================================================
REM  One-command push to GitHub (created by CodeBuddy)
REM  Usage:   github-push.bat ^<github-username^> [repo-name]
REM  Example: github-push.bat panyiran jiayin
REM  NOTE: create an EMPTY repo on github.com first (no README!)
REM ============================================================
setlocal
set "user=%~1"
set "repo=%~2"
if "%user%"=="" (
  echo Usage: github-push.bat ^<github-username^> [repo-name]
  echo Example: github-push.bat panyiran jiayin
  pause
  exit /b 1
)
if "%repo%"=="" set "repo=jiayin"

cd /d "%~dp0"
git remote remove origin >nul 2>&1
git remote add origin https://github.com/%user%/%repo%.git
git push -u origin master
if errorlevel 1 (
  echo.
  echo [FAILED] Check:
  echo   1. Repo https://github.com/%user%/%repo% exists on GitHub
  echo   2. The repo is EMPTY (no README / .gitignore / license)
  echo   3. Browser login window completed
  pause
  exit /b 1
)
echo.
echo === SUCCESS! Pushed to https://github.com/%user%/%repo% ===
echo Next: deploy on render.com (Blueprint) and vercel.com
pause
