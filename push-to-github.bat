@echo off
chcp 65001 >nul
setlocal
title 家音 · 一键推送到 GitHub

echo ========================================
echo   家音 · 一键推送代码到 GitHub
echo ========================================
echo.

REM ---------- 让用户输入信息 ----------
set /p GH_USER="[1/4] 输入你的 GitHub 用户名 (例: panyiran): "
if "%GH_USER%"=="" goto :error_input
set /p GH_EMAIL="[2/4] 输入你的 GitHub 注册邮箱 (例: xxx@163.com): "
if "%GH_EMAIL%"=="" goto :error_input
set /p GH_REPO="[3/4] 输入仓库名 (默认 jiayin-demo): "
if "%GH_REPO%"=="" set GH_REPO=jiayin-demo
set /p COMMIT_MSG="[4/4] 输入提交信息 (默认: 家音 v1.0): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=家音 v1.0 · iCAN参赛版

echo.
echo ----------------------------------------
echo   用户名: %GH_USER%
echo   邮箱:   %GH_EMAIL%
echo   仓库:   %GH_REPO%
echo   信息:   %COMMIT_MSG%
echo ----------------------------------------
set /p CONFIRM="确认无误？(y/n): "
if /i not "%CONFIRM%"=="y" goto :end

REM ---------- 进入项目目录 ----------
set PROJECT_DIR=C:\Users\潘亦然\Desktop\家音.潘
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo [ERROR] 找不到目录 %PROJECT_DIR%
    pause
    exit /b 1
)

REM ---------- 配置 Git 用户身份 ----------
echo.
echo [A] 配置 Git 用户身份...
git config --global user.name "%GH_USER%"
git config --global user.email "%GH_EMAIL%"
echo      完成

REM ---------- 初始化仓库 ----------
echo.
echo [B] 初始化 Git 仓库...
if not exist ".git" (
    git init
    echo      完成
) else (
    echo      已存在 .git，跳过
)

REM ---------- 添加文件 ----------
echo.
echo [C] 添加文件...
git add .
echo      完成

REM ---------- 提交 ----------
echo.
echo [D] 提交...
git commit -m "%COMMIT_MSG%" --allow-empty
echo      完成

REM ---------- 切换到 main 分支 ----------
echo.
echo [E] 切换 main 分支...
git branch -M main

REM ---------- 关联远程仓库 ----------
echo.
echo [F] 关联远程仓库...
set REMOTE_URL=https://github.com/%GH_USER%/%GH_REPO%.git
git remote remove origin 2>nul
git remote add origin "%REMOTE_URL%"
echo      远程地址: %REMOTE_URL%

REM ---------- 推送 ----------
echo.
echo ========================================
echo   即将推送到 GitHub
echo   如弹窗要求登录，请用 GitHub 账号登录
echo   如需密码，请用 Personal Access Token
echo ========================================
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ========================================
    echo   推送失败，可能原因：
    echo   1. 仓库还没创建（先去 GitHub 建一个）
    echo   2. 没连网络
    echo   3. 凭据错误（用 Personal Access Token）
    echo.
    echo   解决方案见 DEPLOY_STEPS.md 第 3.5 步
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo   🎉 推送成功！
echo.
echo   仓库地址：%REMOTE_URL%
echo   下一步：打开 Render 按 DEPLOY_STEPS.md 第 4 步继续
echo ========================================
pause
goto :end

:error_input
echo [ERROR] 信息不能为空
pause
exit /b 1

:end
endlocal