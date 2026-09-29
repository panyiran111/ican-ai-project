# Vercel 部署说明（前端 Vue3 SPA）

## 项目结构
- 仓库根目录：`C:\Users\潘亦然\Desktop\家音.潘\`
- 前端代码：`frontend/`
- 静态构建产物：`frontend/dist/`

## Vercel 控制台配置（Web 端点点点）

### 1. New Project
1. 登录 https://vercel.com → "Add New → Project"
2. 选你的 GitHub 仓库（推荐：`xxx/jiayin`，仓库名保持英文，不要含 `.` 否则会有问题）

### 2. Configure Project（关键！）
- **Framework Preset**：选 `Vite`（自动识别）
- **Root Directory**：点 `Edit` → 选 `frontend`（必须，不选会失败）
- **Build Command**：`npm run build`（自动填好）
- **Output Directory**：`dist`（自动填好）

### 3. Environment Variables（关键！）
在 "Environment Variables" 添加：
```
VITE_API_BASE = https://你的Render后端地址.onrender.com
```
> ⚠️ 不要带末尾斜杠！不要带 `/api`！

勾选：Production / Preview 都启用。

### 4. Deploy
- 点 Deploy → 等 1-2 分钟 → 拿到 `xxx.vercel.app` 域名
- **绑定域名**（可选）：Settings → Domains → 添加 `jiayin.xxx.com`

## 配置文件
- `vercel.json`：本仓库根目录，定义 Vite 框架 + SPA 路由 fallback + 静态资源缓存

## 自定义域名
- 已在 Vercel 配置后无需其他操作
- DNS：在域名注册商添加 CNAME 指向 `cname.vercel-dns.com`

## 故障排查

| 问题 | 原因 | 解决 |
|---|---|---|
| 部署后页面空白 | 选了根目录而非 frontend/ | Vercel → Settings → Root Directory 改 `frontend` |
| API 请求 404 | VITE_API_BASE 没填 | 环境变量检查 |
| API 请求 CORS 报错 | 后端 allow_origins=* 已开，正常 |
| 慢点击 npm install | Vercel 默认就会 npm install |
| 二次刷新页面 404 | SPA 路由问题 | 已配 `vercel.json` rewrites，无需再处理（其实用了 HashHistory 用不上，但加上更稳） |

## 自动部署
- push 到 main 分支 → 自动重新部署
- PR 会生成 Preview 链接（可分享给评委看 Demo）

## 提示
- 后端 Render 免费版冷启动 30-60s，第一次访问会慢一点
- Vercel 全球 CDN，极快
- 配合使用：Render 后端 + Vercel 前端 → 全球可用