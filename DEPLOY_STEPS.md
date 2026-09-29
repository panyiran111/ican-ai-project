# 家音 · 推送代码到永久网址 · 全步骤零基础手册（30 分钟完成）

> 📍 路径：`C:\Users\潘亦然\Desktop\家音.潘\`
> 🎯 最终目标：拿到永久网址 `https://xxx.vercel.app` 给评委
> ⏱ 预计时间：30 分钟（首次操作）

---

## 📑 总览流程

| 步骤 | 工具 | 时间 |
|---|---|---|
| 第 1 步 | 注册/登录 GitHub | 2 分钟 |
| 第 2 步 | 创建 GitHub 仓库 | 1 分钟 |
| 第 3 步 | 推送代码到 GitHub | 5 分钟 |
| 第 4 步 | Render 部署后端 | 10 分钟 |
| 第 5 步 | Vercel 部署前端 | 5 分钟 |
| 第 6 步 | 验收 + 填回 README | 5 分钟 |

---

## 第 1 步 · 注册/登录 GitHub（2 分钟）

### 1.1 打开 GitHub
- 浏览器地址栏输入：`https://github.com`
- 如果已经有账号：右上角 `Sign in` → 输入邮箱密码登录
- 如果没账号：右下角 `Create an account` → 按提示填用户名/邮箱/密码

### 1.2 验证邮箱
- GitHub 会发一封验证邮件到你的注册邮箱
- **必须点开邮件里的验证链接**，否则后面创建仓库会被卡

### 1.3 ⚠️ 建议：把账号升级成"个人免费"
- 登录后右上角头像 → `Emails` → 确认主邮箱已验证
- Settings → `Billing and plans` → 确认是 `Free`（免费计划）

---

## 第 2 步 · 创建 GitHub 仓库（1 分钟）

### 2.1 创建新仓库
- 登录后右上角 **`+`** 号 → **`New repository`**

### 2.2 填写仓库信息（**所有选项都按这个填**）

| 选项 | 填什么 | 说明 |
|---|---|---|
| **Repository name** | `jiayin-demo` | ⚠️ 全小写英文短横线，不要用「家音.潘」 |
| **Description** | `家音 · AI家庭沟通翻译官 · iCAN参赛作品` | 可选 |
| **Public / Private** | `Public` ⚠️ | 必须选 Public，Render/Vercel 免费版要求 |
| **Add a README file** | ☐ **不勾选** | 我们本地已有代码了 |
| **Add .gitignore** | ☐ **不勾选** | 本地已有 |
| **Choose a license** | 选 `MIT License` | 可选，方便开源 |

### 2.3 创建
- 拉到最下面 → 绿色按钮 **`Create repository`**

### 2.4 复制仓库地址
- 创建完会跳到一个页面，**复制那个 HTTPS 地址**
- 形如：`https://github.com/你的用户名/jiayin-demo.git`
- ⚠️ **把"你的用户名"和"jiayin-demo"记下来**（第 3 步要用）

---

## 第 3 步 · 推送代码到 GitHub（5 分钟）

### 方式 A · 命令行（推荐，最快）

#### 3.1 打开 PowerShell
- 按 `Win + R` → 输入 `powershell` → 回车
- 进入项目目录：
```powershell
Set-Location "C:\Users\潘亦然\Desktop\家音.潘"
```

#### 3.2 配置 Git 用户身份（**首次使用必做**）
把下面命令里的 `你的名字` 和 `你的邮箱` **改成你自己的**（用 GitHub 注册的邮箱）：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@xxx.com"
```
> 例如：`git config --global user.name "潘亦然"`
> 例如：`git config --global user.email "panyiran@163.com"`

#### 3.3 初始化并提交
```powershell
git init
git add .
git commit -m "家音 v1.0 · iCAN参赛版"
```
> 如果 `.git` 已存在会报 `Reinitialized`，正常可忽略
> commit 完成会列出几十个文件被提交

#### 3.4 连接到 GitHub 并推送
把第 2 步复制的那串地址粘进来（**替换成你自己的**）：

```powershell
git remote add origin https://github.com/你的用户名/jiayin-demo.git
git branch -M main
git push -u origin main
```

#### 3.5 输入 GitHub 凭据
弹出登录窗口：
- 浏览器自动弹出 → 登录 GitHub → 点 **`Authorize git-credential-manager`**
- 或：用户名输 GitHub 登录名，密码输 **Personal Access Token**（不是登录密码）

> ⚠️ 如果推送失败要求密码：
> 1. GitHub 右上角头像 → `Settings`
> 2. 最下面 `Developer settings`
> 3. `Personal access tokens` → `Tokens (classic)` → `Generate new token`
> 4. 勾选 `repo` 全选 → 点 `Generate token`
> 5. **复制那个 token 字符串**（只显示一次！）
> 6. 用这个 token 当密码再 push 一次

#### 3.6 验证
- 刷新 GitHub 仓库页面
- 应该能看到几十个文件已上传 ✅

---

### 方式 B · GitHub Desktop（点点点，不想用命令行的选这个）

#### 3.1 下载安装
- https://desktop.github.com → 下载 → 安装 → 登录

#### 3.2 添加本地仓库
- File → **`Add Local Repository`** → 选 `C:\Users\潘亦然\Desktop\家音.潘`
- 如果提示「这不是 git 仓库」→ 选 `create a repository`

#### 3.3 提交
- 左下角 Summary 填：`家音 v1.0 · iCAN参赛版`
- Description 可选
- 点 `Commit to main`

#### 3.4 发布到 GitHub
- 顶部工具栏 **`Publish repository`** 按钮
- Name 填 `jiayin-demo`
- 取消勾选 `Keep this code private`（必须公开）
- 点 `Publish Repository`

---

## 第 4 步 · Render 部署后端（10 分钟）

### 4.1 注册 Render
- 浏览器打开：`https://render.com`
- 右上角 **`Get Started for Free`** 或 **`Sign In`**
- 选 **`GitHub`** 一键登录（最方便）

### 4.2 创建 Blueprint 服务
- 登录后右上角 **`New +`** → **`Blueprint`**
- 第一次会让你授权 Render 访问 GitHub → 全部勾选 → `Install & Authorize`
- 选你的仓库 **`jiayin-demo`**
- 点 **`Apply`**

### 4.3 等构建（约 5-8 分钟）
- 状态会从 `deploying` → `live`
- **构建日志**会显示 `pip install` → `==> Build successful` → `Deploying`

### 4.4 复制后端地址
- 服务跑起来后，页面顶部会有 **`Your service is live at https://xxx.onrender.com`**
- ⚠️ **完整复制这个地址（包含 https://）**
- 形如：`https://jiayin-api-abc123.onrender.com`

### 4.5 测试后端
- 浏览器直接打开：`https://你的后端地址/api/health`
- 应该看到：
  ```json
  {"status":"ok","service":"jiayin","llm_ready":false}
  ```
- **第一次可能要刷新 2-3 次**（免费版冷启动 30-60 秒）

### 4.6 （可选）配置大模型 API Key
- 后端目前用演示剧本，不填 Key 也能跑（比赛够用）
- 如果想用真实 AI：在 Render 服务页面 → `Environment` → `Add Environment Variable`：
  ```
  Key: LLM_API_KEY        Value: 你的deepseek_key
  Key: LLM_BASE_URL       Value: https://api.deepseek.com
  Key: LLM_MODEL          Value: deepseek-chat
  ```
- 改完会自动重新部署

---

## 第 5 步 · Vercel 部署前端（5 分钟）

### 5.1 注册 Vercel
- 浏览器打开：`https://vercel.com`
- 右上角 **`Sign Up`** → 选 **`Continue with GitHub`** 一键登录

### 5.2 创建项目
- 登录后会自动跳到 Dashboard（或点 https://vercel.com/dashboard）
- **`Add New...`** → **`Project`**
- **`Import`** 你刚创建的 `jiayin-demo` 仓库
- 如果没看到，点 `Adjust GitHub App Permissions` → 把仓库勾上

### 5.3 ⚠️ 配置项目（这一步最关键，90% 失败都在这）

#### 5.3.1 Project Name
- 保持默认 `jiayin-demo` 或改英文短横线名

#### 5.3.2 Framework Preset
- 自动识别成 **`Vite`** ✅ 不要改

#### 5.3.3 Root Directory（⚠️ 必改）
- 点 **`Edit`** 按钮
- 在弹窗里选 **`frontend`**
- ⚠️ **必须改，不改会部署失败或白屏**

#### 5.3.4 Build and Output Settings
- Build Command：`npm run build`（自动填好）
- Output Directory：`dist`（自动填好）
- Install Command：`npm install`（自动填好）

### 5.4 ⚠️ 配置环境变量（这一步必填，否则 API 请求会失败）

展开 **`Environment Variables`**：

| Name | Value |
|---|---|
| **`VITE_API_BASE`** | **`https://你的后端地址.onrender.com`** |

填法：
- Name 输入框：`VITE_API_BASE`
- Value 输入框：粘第 4 步复制的那串地址
- ⚠️ **不要带末尾斜杠**！
- ⚠️ **不要带 /api 后缀**！只填域名根

下方三个选项全部勾选：
- ☑ Production
- ☑ Preview
- ☑ Development

### 5.5 部署
- 点蓝色按钮 **`Deploy`**
- 等 1-3 分钟：会显示 `Building` → `Deploying` → `Visit` 🎉

### 5.6 复制前端地址
- 部署完成会显示：
  ```
  🎉 Your project has been successfully deployed.
  https://jiayin-demo-xxxx.vercel.app
  ```
- **复制这个地址** → 这是给评委的永久链接

---

## 第 6 步 · 验收（5 分钟）

### 6.1 打开前端地址
浏览器打开 `https://你的xxx.vercel.app`，应该看到：
- [ ] 家音首页加载（不是白屏）
- [ ] 小人挥手打招呼动画
- [ ] 底部 5 个 Tab 可见

### 6.2 验收 5 个核心页面（每个都点一下）

| 页面 | 验收动作 | 期望结果 |
|---|---|---|
| **首页** | 看小人和今日卡 | 展示你之前用过的小档案/打卡数据 |
| **关心解码器** | 粘贴一段养生文 → 点「翻译关心」 | 30-60 秒内返回核心/情感/意图 |
| **回音壁** | 切 tough/normal/sweet | 三种不同语气回复 |
| **连心话题卡** | 切场景（回家前/节日/生日/普通） | 各 5 个话题 |
| **彩排室** | 选「挂科了」→ 跟 AI 妈对一轮 | 多轮对话能继续 |
| **安心打卡** | 上传一张照片 → 写一句话 | 安心值+1 |
| **合养小宠物** | 看成长值 | 显示你之前的成长记录 |

### 6.3 ⚠️ 性能提示
- 后端第一次访问会冷启动 30-60 秒
- 评委点开链接时如果「正在加载」，请他们等几十秒再试
- （可在快手视频简介写「首次打开需等待 30 秒冷启动」）

---

## 第 7 步 · 填回 README（1 分钟）

### 7.1 编辑 README.md
打开 `C:\Users\潘亦然\Desktop\家音.潘\README.md`，找到「在线体验」一节（约第 47 行）：

```markdown
## 在线体验
- 前端（Vercel）：https://____.vercel.app
- 后端 API（Render）：https://____.onrender.com
```

把 `____` 替换成你的真实地址。

### 7.2 推送更新
```powershell
Set-Location "C:\Users\潘亦然\Desktop\家音.潘"
git add README.md
git commit -m "更新线上 demo 地址"
git push
```

Render 和 Vercel 会自动重新部署（但内容没变，只是同步 README）。

---

## 🎉 大功告成！

你现在手上有了：
- ✅ **永久前端网址**：`https://你的xxx.vercel.app`（给评委的链接就是这个）
- ✅ **永久后端地址**：`https://你的xxx.onrender.com`（API 接口地址）

### 给评委的最简消息
```
家音 · AI 家庭沟通翻译官
在线体验：https://你的xxx.vercel.app

核心功能：
1. 关心解码器：把爸妈的养生文翻译成他们没说出口的关心
2. 回音壁：三档语气帮你回消息
3. 彩排室：AI 扮演爸妈，跟你练习难开口的话题
4. 连心话题卡：4 场景 5 个问题，再也不尬聊
5. 安心打卡 + 合养小宠物：让爸妈看到你的日常

作品说明：iCAN 大学生创新创业大赛 · AI 产品实现方向
视频：https://快手视频链接
```

---

## 🆘 排错速查

| 症状 | 原因 | 解决 |
|---|---|---|
| git push 弹窗输密码失败 | GitHub 已禁用密码登录 | 用 Personal Access Token |
| Render 部署 Build failed | render.yaml 路径错 | 确认 `rootDir: backend` |
| Render 部署后 API 502 | 还在构建中 | 等 1-2 分钟 |
| Vercel 部署后白屏 | Root Directory 没改 | Settings → Root Directory → 改 `frontend` → Redeploy |
| Vercel API 请求 404 | VITE_API_BASE 没填或填成项目名 | 改成完整后端地址 |
| Vercel 部署后 API 502 | 后端冷启动中 | 等 30-60 秒 |
| 路由刷新 404 | SPA fallback 缺 | `vercel.json` 已配，正常不该出现 |

---

## ⚡ 30 秒快速通道（已经做过的人）

如果你已经注册过 GitHub/Render/Vercel 并配过 SSH：

```powershell
Set-Location "C:\Users\潘亦然\Desktop\家音.潘"
git init
git add .
git commit -m "家音 v1.0"
git remote add origin https://github.com/你的用户名/jiayin-demo.git
git push -u origin main
# 然后 Render → Blueprint → 选仓库 → Apply
# 然后 Vercel → Import → Root Directory=frontend → VITE_API_BASE=你的后端 → Deploy
```

---

祝部署顺利！🚀 拿到永久网址后随时叫我下一步。