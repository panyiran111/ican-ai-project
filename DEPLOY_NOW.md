# 家音 · 部署上线操作手册（D3 Step 1 · 今天就发链接）

> 📍 当前进度：代码 ✅ / 演示视频 ✅ / 产品说明书 ✅ / **部署 ← 你现在在这里**
> 🎯 目标：评委点开 `https://xxx.vercel.app` 就能看到完整 demo

---

## 0. 准备工作（5 分钟，一次性）

| 准备项 | 说明 |
|---|---|
| GitHub 账号 | 没有去 https://github.com 注册 |
| 仓库 | 在 GitHub 建一个空仓库（公开），名字例如 `jiayin-demo` |
| 本地 Git | 安装 Git for Windows（如果还没装）|

---

## 1. 推送代码到 GitHub（5 分钟）

### 方式 A：用 GitHub Desktop（最省心，点点点）
1. 下载安装 https://desktop.github.com
2. File → New Repository → Name=`jiayin-demo` → Local Path 选 `C:\Users\潘亦然\Desktop\家音.潘`
3. 点 "Publish to GitHub"

### 方式 B：命令行（如果已经装了 Git）
```powershell
Set-Location "C:\Users\潘亦然\Desktop\家音.潘"
git init
git remote add origin https://github.com/你的用户名/jiayin-demo.git
git add .
git commit -m "家音 v1.0 · iCAN 参赛版"
git branch -M main
git push -u origin main
```

> ⚠️ `.gitignore` 已经排除 `.venv` / `node_modules` / `.env`，不会泄露 API Key

---

## 2. 部署后端到 Render（10 分钟）

### 步骤 2.1 · 创建服务
1. 打开 https://render.com → 用 GitHub 登录
2. 右上角 `New +` → `Blueprint`
3. 连 GitHub 授权 → 选你的 `jiayin-demo` 仓库
4. Render 自动读取根目录的 `render.yaml` → 显示一个 `jiayin-api` 服务
5. 点 `Apply` → 等 5-10 分钟

### 步骤 2.2 · 验证后端
访问 `https://jiayin-api-xxx.onrender.com/api/health`
应该看到：
```json
{"status":"ok","service":"jiayin","llm_ready":false}
```
> 第一次访问会等 30-60 秒（免费版冷启动），多刷新几次就行

### 步骤 2.3 · 复制后端地址
形如：`https://jiayin-api-xxxx.onrender.com`（**记下来**，下一步要用）

---

## 3. 部署前端到 Vercel（5 分钟）

### 步骤 3.1 · 创建项目
1. 打开 https://vercel.com → 用 GitHub 登录
2. `Add New → Project` → 选 `jiayin-demo` 仓库
3. 点 `Import`

### 步骤 3.2 · 配置项目（最关键）
| 选项 | 值 |
|---|---|
| Framework Preset | Vite（自动识别） |
| **Root Directory** | **点 Edit → 选 `frontend`** ⚠️ |
| Build Command | `npm run build` |
| Output Directory | `dist` |

### 步骤 3.3 · 配置环境变量（最关键 ⚠️）
展开 "Environment Variables"，添加：
```
VITE_API_BASE = https://jiayin-api-xxxx.onrender.com
```
> ⚠️ **不要带末尾斜杠**！**不要带 `/api`**！只填域名根
> Production / Preview / Development 三个选项都勾选

### 步骤 3.4 · 部署
1. 点 `Deploy`
2. 等 1-2 分钟 → 拿到 `https://jiayin-demo-xxx.vercel.app`

### 步骤 3.5 · 验证
打开 `https://jiayin-demo-xxx.vercel.app`
- ✅ 应该看到家音首页
- ✅ 小人挥手打招呼
- ✅ 切到关心解码器 → 输入 → 点「翻译关心」
- ✅ 30 秒后看到结果（后端冷启动）

---

## 4. 更新 README.md（1 分钟）

打开 `README.md`，找到「在线体验」一节，把两个地址填进去：
```markdown
## 在线体验
- 前端（Vercel）：https://jiayin-demo-xxx.vercel.app
- 后端 API（Render）：https://jiayin-api-xxxx.onrender.com
```

提交代码：
```powershell
git add README.md
git commit -m "更新线上地址"
git push
```
Vercel 和 Render 会自动重新部署。

---

## 5. 给评委的链接（最后一步）

**主链接**：`https://jiayin-demo-xxx.vercel.app`

把这个链接 + 一句话说明发到：
- 比赛报名表单的「产品实现方向—其他辅助材料」备注里
- 微信群 / 朋友圈 / 比赛交流群
- 快手视频简介里（"完整 demo 在线体验：xxx.vercel.app"）

---

## ⚡ 快速排错

| 问题 | 解决 |
|---|---|
| Render 部署失败 ModuleNotFound | 检查 backend/requirements.txt 是否推送 |
| Vercel 部署后白屏 | Root Directory 必须选 frontend/ |
| Vercel API 请求 404 | VITE_API_BASE 没填或填错（不要带 /api）|
| Vercel 部署后 API 502 | Render 还在冷启动，等 60 秒 |
| 路由刷新 404 | 用了 HashHistory，正常不应该出现；如果出现检查 vercel.json |

---

## 🆘 应急方案：本地 + cloudflared 临时公网链接

如果永久部署来不及，可让评委先看临时链接（要求你电脑不关机）：

### 步骤 · 1 分钟
1. 下载 cloudflared：https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
2. 放到 `C:\Users\潘亦然\Desktop\家音.潘\` 下
3. 确认本地后端(:8000)和前端(:4173)都跑着
5. 双击运行：
```powershell
cd C:\Users\潘亦然\Desktop\家音.潘
.\cloudflared-windows-amd64.exe tunnel --url http://127.0.0.1:4173
```
6. 控制台会输出一个 `https://xxx.trycloudflare.com` 链接 → 把这个发给评委

> ⚠️ **临时链接关电脑就没了**，仅作为提交前的应急备用
> 评委看完后，正式版开始正式版 → Render + Vercel（永久）

---

## ✅ 完成自检（提交前最后一遍）

- [ ] 打开 `https://你的前端.vercel.app` → 首页能加载
- [ ] 切到「关心解码器」→ 输入"妈今天又转养生文" → 点翻译 → 看到结果（30秒内）
- [ ] 切到「回音壁」→ 选 tough/normal/sweet → 看到三档回复
- [ ] 切到「连心话题卡」→ 看到 5 个话题
- [ ] 切到「彩排室」→ 选"挂科了"→ 跟 AI 妈对一轮
- [ ] 切到「安心打卡」→ 选照片→看到安心值
- [ ] 切到「合养小宠物」→ 看到成长值（你应该有几个，因为之前用过）
- [ ] 「我家小档案」填一次 → 提示词带出"酸菜鱼"等个性化

---

最后祝提交顺利！🎉