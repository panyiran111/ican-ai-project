# D3 Step 1 · 部署上线操作指引

> 项目：家音 Jiayin（2026 iCAN · 9月月赛）
> 日期：2026-09-27
> 方案：后端 Render（免费）+ 前端 Vercel（免费），需一个 GitHub 账号

---

## ✅ 已完成的代码改造（本轮完成，全部通过本地验证）

| 改造 | 文件 | 说明 |
|---|---|---|
| API 地址统一出口 | `frontend/src/api.js`（新增） | `VITE_API_BASE` 环境变量控制，本地为空走代理，线上直连后端 |
| 6 处 fetch 改造 | `DecodeView / ReplyView / TopicView / RehearsalView` | `fetch('/api/x')` → `fetch(apiUrl('/api/x'))` |
| Vite 代理可配置 | `frontend/vite.config.js` | 代理目标支持环境变量覆盖 |
| 环境变量模板 | `frontend/.env.development` / `.env.production` | 生产值在 Vercel 控制台注入（优先级高于文件，不会忘改） |
| Render 一键部署配置 | `render.yaml`（根目录，新增） | Blueprint：Python 3.11 + uvicorn，健康检查 `/api/health` |
| Git 忽略清单 | `.gitignore`（根目录，新增） | 排除 `.venv` / `node_modules` / `dist` / `.env` / 日志 |
| README 在线体验段 | `README.md` | 已留前后端地址占位符 + 部署说明 |

**本地验证结果：**
- 前端 `npm run build` 构建成功，产物无占位符泄漏
- 后端回归：彩排室 7 项 / 画像 2 项 / 打卡 15 项 全部 PASS
- 前端代理链路：`localhost:5173` 页面 200，`/api/health` 经代理正确到达后端

---

## ⚠️ 你需要先做的一件事：安装 Git + 推 GitHub

**本机未安装 Git**（Render / Vercel 都从 GitHub 拉代码）。最简单方式：

1. 下载安装 **GitHub Desktop**：https://desktop.github.com （自带 Git，图形界面）
2. 安装后登录 GitHub 账号（没有就注册一个，免费 2 分钟）
3. 在 GitHub Desktop 中：`File → Add local repository → Choose` 选择 `C:\Users\潘亦然\Desktop\家音.潘`
   - 提示 "not a Git repository" → 点 **create a repository** → 名称建议 `jiayin`，**保持 Public（公开）**
4. 点 **Publish repository** 推到 GitHub

---

## 第一步 · 后端 → Render（约 10 分钟）

1. 打开 https://render.com → 用 GitHub 账号登录
2. 控制台点 **New → Blueprint**
3. 选择刚发布的 `jiayin` 仓库 → Render 会自动读取根目录 `render.yaml`
4. 直接 **Apply**（`LLM_API_KEY` 留空即可，无 Key 自动降级演示剧本，Demo 永不翻车）
5. 等待构建完成（首次约 3-5 分钟），得到地址：`https://jiayin-api.onrender.com`
6. 验证：浏览器打开 `https://jiayin-api.onrender.com/api/health`，应返回 `{"status":"ok",...}`
   - 如果想接大模型：Render 控制台 → jiayin-api → Environment → 添加 `LLM_API_KEY`（DeepSeek / 通义千问 / 智谱均可，见 `backend/.env.example`）

## 第二步 · 前端 → Vercel（约 5 分钟）

1. 打开 https://vercel.com → 用 GitHub 账号登录
2. **Add New → Project** → 导入 `jiayin` 仓库
3. 关键设置：
   - **Root Directory：`frontend`**
   - Framework Preset：自动识别 Vite
   - **Environment Variables → 添加：**
     - Name：`VITE_API_BASE`
     - Value：`https://jiayin-api.onrender.com`（上一步的后端地址，末尾不带斜杠）
4. **Deploy** → 等约 1 分钟，得到 `https://jiayin-xxx.vercel.app`

## 第三步 · 端到端验证（5 分钟，务必做）

打开线上前端地址，依次验证：

- [ ] 首页正常渲染（打卡横幅 + 四个功能入口）
- [ ] 解码器：贴示例 → 「翻译这份关心」→ 出结果
- [ ] 回音壁：生成三档回复 + 一键复制
- [ ] 话题卡：抽 5 张
- [ ] 彩排室：开一局聊 2 轮
- [ ] 手机浏览器再过一遍（语音功能需 Chrome/Edge + https，Vercel 自带 https ✅）

> Render 免费版 15 分钟无请求会休眠，**首次打开冷启动 30-60 秒**（演示前先点一次预热）。休眠只影响彩排室会话（内存丢失），其余功能无状态不受影响——与《明天继续.md》已知取舍一致。

## 第四步 · 收尾

1. 把两个线上地址回填 `README.md` 的「在线体验」占位符
2. 提交推送（GitHub Desktop → Commit → Push origin）
3. 之后每次改代码 push，Vercel / Render 自动重新部署

---

## 备选方案（如评委/国内访问 Vercel 慢）

- 前端改用 **EdgeOne Pages**（腾讯，免费，国内快）：导入同一 GitHub 仓库，构建命令 `npm run build`，输出目录 `frontend/dist`，环境变量同 `VITE_API_BASE`
- 后端国内备选：阿里云函数计算 / 腾讯云 CloudBase 云函数（FastAPI 可直接部署）

---

## 明日接续（D3 Step 2-4）

- Step 2 演示视频：3-5 分钟录屏，脚本见《明天继续.md》
- Step 3 作品说明书：素材 README + docs/diagrams.md + docs/progress.md
- Step 4 核对官方提交清单（去大赛报名页找格式要求）

**完成后把这一页和 README 一起交给明天的你。加油。**
