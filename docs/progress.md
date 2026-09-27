# 家音 · 开发进度

## D1（9/23）上午 —— ✅ 完成

### 已完成
- 项目骨架：`jiayin/frontend`（Vue3+Vite+Vant，5页面路由+底部导航）+ `jiayin/backend`（FastAPI）
- 后端可运行：`/api/health`、`/api/decode`（关心解码器，两段式提示词已就位，无 Key 自动降级演示数据）
- 前端可运行：首页 + 解码器页（含3组示例一键填充），回音壁/彩排室/话题卡为占位页
- 环境问题已解决：
  - 系统 Python 3.7 过旧 → 用 `py -3.10` 建 venv（`backend/.venv`）
  - 系统无 Node → 便携版 Node v20.18.0 解压在 `20260922211024/node-v20.18.0-win-x64/`
  - 修复 `llm.py` 中文引号嵌套导致的 SyntaxError

### 当前运行方式
```powershell
# 后端（已在跑，如重启）：
cd jiayin/backend ; .\.venv\Scripts\python.exe -m uvicorn main:app --port 8000

# 前端（已在跑，如重启）：
$env:PATH = "c:\Users\潘亦然\CodeBuddy\20260922211024\node-v20.18.0-win-x64;" + $env:PATH
cd jiayin\frontend ; npm run dev   # http://localhost:5173
```
或直接运行 `jiayin/frontend/dev.bat`

### 待用户验收
- 浏览器打开 http://localhost:5173 查看首页/解码器
- 待办：申请大模型 API Key 填入 `jiayin/backend/.env`

## D1 下午 —— ✅ 完成

- 演示剧本引擎升级：`llm.py` 内置 10 类场景剧本（养生文/回家/熬夜/降温/生活费/对象/寄药/早晚安问候/工作/讲座）+ 默认兜底，关键词匹配命中；已实测三类输入精准命中三个场景
- `docs/diagrams.md`：三张 Mermaid 流程图（用户旅程/系统架构/解码器技术流程），贴 mermaid.live 可导出 PNG
- 无 API Key 全功能可跑（安全路线）；拿到 Key 后填 `.env` 即平滑切换真实大模型

## D2 —— 进行中

### Step 1 · 回音壁 —— ✅ 完成（9/23 晚）
- 后端 `llm.py`：新增 `reply_care()` 主入口 + `REPLY_SYSTEM_PROMPT`（三档语气：嘴硬 tough/标准 normal/撒娇 sweet，≤60 字、微信口语化、不辟谣）+ `DEMO_REPLY_SCENARIOS` 10 场景 × 3 档演示剧本 + `DEMO_REPLY_DEFAULT` 兜底
- 后端 `main.py`：新增 `ReplyRequest`（content + tone）+ `POST /api/reply`
- 前端 `ReplyView.vue` 重写：输入区（3 个示例 chips）+ 子女画像三选一卡片（嘴硬/标准/撒娇）+ 三档并列结果卡片 + 一键复制（clipboard API + execCommand 双兜底）
- 关键词去重：去掉通用词"养生""五点"，避免养生文/讲座场景互窜（10 场景 + 兜底全部实测命中）
- 端到端实测：后端 :8000 / 前端 :5173 / Vite 代理 `/api/reply` 全部 200
- 注意：CodeBuddy 沙箱里 npm 不在 PATH，启动前端需用便携 Node：
  `C:\Users\潘亦然\CodeBuddy\20260922211024\node-v20.18.0-win-x64\node.exe frontend\node_modules\vite\bin\vite.js`

### Step 2 · 连心话题卡 —— ✅ 完成（9/24）
- 后端 `llm.py`：新增 `topic_care()` 主入口 + `TOPIC_SYSTEM_PROMPT`（5 个开放性问题：问爸妈自己的生活、具体有烟火气、非是否题、至少 1 个带子女自己入局、不说教）+ `DEMO_TOPIC_SCENARIOS` 4 场景（回家前/节日/生日/普通通话）× 5 条保底话题
- 后端 `main.py`：新增 `TopicRequest` + `POST /api/topic` + `GET /api/topic/scenes`
- 前端 `TopicView.vue` 重写：2×2 场景选择卡片（🏠回家前/🥮节日/🎂生日/📞普通通话）+「抽 5 张话题」按钮 + 话题卡片逐张翻转入场动画（flipIn + 逐张 0.12s 延迟）+ 每条一键复制 + 使用小贴士
- 兜底：未知 scene 自动落到「普通通话」；LLM 返回 topics 非法/为空时回退保底话题
- 端到端实测：4 场景 + 未知场景兜底全部命中（「回家前」首条即"爸最近那盘棋下得怎么样了"）；:8000 / :5173 / Vite 代理 `/api/topic` 全部 200

### Step 3 · 彩排室 —— ✅ 完成（9/24）
- 后端 `llm.py`：新增彩排室会话引擎 —— `rehearsal_start()`（创建会话 + 爸妈开场白）/ `rehearsal_chat()`（多轮对话，内存会话表 `REHEARSAL_SESSIONS`，上限 200 个自动淘汰最老）
- `REHEARSAL_SYSTEM_PROMPT`：AI 爸妈人设（接地气有烟火气、先心疼不质问、不说教、主动托底「爸养你两个月」、每轮 ≤80 字、从心疼推进到出主意）
- `DEMO_REHEARSAL_SCENARIOS`：4 场景 × 5 轮剧本（挂科了/妈妈、分手了/妈妈、想辞职/爸爸、生活费不够/妈妈）+ 兜底台词循环；LLM 模式带完整 history 调用，异常自动降级剧本
- 后端 `main.py`：`POST /api/rehearsal/start` + `POST /api/rehearsal/chat`（无效会话 404）+ `GET /api/rehearsal/scenes`
- 前端 `RehearsalView.vue` 重写：场景四宫格 → 聊天界面（爸妈头像气泡 + 自己渐变气泡 + 打字三点动画 + Enter 发送 + 自动滚底 +「换场景重来」）
- 自测通过（`backend/test_rehearsal.py`，保留作回归用）：挂科了场景妈妈先心疼（"没事没事，先别急，天塌不下来"）再问情况，剧本走完兜底台词续聊，404/未知场景兜底均正确；Vite 代理 `/api/rehearsal/*` 全 200
- 注意：shell 为 PowerShell，`cd /d` 是 cmd 语法会报错，需用 `Set-Location`

### Step 4 · 联通 & 上线准备 —— ✅ 完成（9/24）
- 三模块串联通路：
  - 解码器结果卡新增「💬 听懂了，去回音壁生成回复 →」按钮，`router.push('/reply?c=原文')` 携带原文
  - 回音壁 `onMounted` 读取 `query.c` 自动预填输入框（截断 2000 字）
  - 回音壁结果尾部 + 话题卡 tips 新增「去彩排室练一遍 →」跳转
- `README.md`：功能全部标 ✅、目录结构更新（含 `test_rehearsal.py`）、新增 API 一览表（7 个端点）
- D3 待办：部署上线（Render / Vercel / 阿里云函数任选其一），`.env` 填入真实 LLM Key

## D2.5 · 冲奖增强 —— ✅ 完成（9/24 晚）

### 每日安心打卡（用户提出，产品留存核心）
- `store/checkin.js`：照片压缩（canvas 640px/jpeg 0.7）base64 存储（上限 90 天）、连续天数计算、同日覆盖、徽章体系（3 冒芽/7 小灶火/21 习惯成/50 心意石/90 长情奖）、安心值（streak/21 封顶 100%）、温柔断签文案
- `CheckinView.vue`（路由 `/checkin`）：状态卡（🔥连击 + 安心值进度条 + 下一徽章预告）、相机/相册打卡（`input[type=file]` H5 通用）、徽章墙（未解锁灰化）、时间轴足迹（今天/昨天/日期）
- 首页横幅：连击数 + 温柔断签提示 + 今日照片缩略图，已打卡变绿色系
- 产品差异化表达：streak 包装为「爸妈已连续 N 天知道你很好」而非「我坚持了 N 天」；断签不惩罚（「昨天断了，没关系，今天重新开始就好」）
- 单测 `backend/test_checkin.py`（Node 模拟 localStorage，15 项全过）：空状态/同日覆盖/3 连击/断签重置/徽章边界/安心值封顶

### 我家小档案（爸妈画像，专属感核心）
- 前端 `store/profile.js`：6 项画像（称呼×2/老家/拿手菜/爸爸爱好/宠物）localStorage 持久化 + `profileSummary()` 摘要
- `components/ProfilePopup.vue`：底部弹层表单，首页 Hero 区入口（未填写引导 / 已填写展示摘要可修改）
- 后端：`/api/decode`、`/api/reply`、`/api/topic` 均支持可选 `profile` 字段；LLM 模式注入提示词（「这个家的专属信息」块）；演示模式做细节替换（排骨→拿手菜、下棋→爸爸爱好）
- 演示剧本加钩子：养生文 normal/sweet 档带"排骨"钩子，确保最常见场景也能被画像个性化
- 自测（`backend/test_profile.py` 保留）：无画像输出"馋你做的排骨了"，画像（酸菜鱼/钓鱼）输出"馋你做的酸菜鱼了""爸最近钓到大家伙了没？"，旧词零残留

### 语音输入 + 朗读（Web Speech API）
- `composables/useSpeech.js`：`useRecognition()`（说话→文字，zh-CN、continuous、实时 interim 追加、权限拒绝提示、组件卸载自动停止）+ `useSpeaker()`（文字→朗读，播放/停止切换态、卸载自动取消）+ `recognitionSupported()` 环境探测
- 不支持的浏览器优雅降级：toast 提示「建议用 Chrome / Edge」，不白屏不报错
- 解码器：输入框旁麦克风按钮（录音中红色脉冲动画 + 「正在听你说…」提示）
- 回音壁：麦克风 + 三档卡片各带「朗读/停止」按钮（朗读中按钮变红可停）
- 纯前端实现零后端改动、零新依赖；注意 http://localhost 下 Chrome 允许麦克风，非安全上下文（如局域网 IP）会受限

### 最近的家音（使用历史）
- 前端 `store/history.js`：localStorage 最近 50 条（decode/reply/topic/rehearsal 四类，含完整 detail 供回看）
- 首页新增「📔 最近的家音」列表（最近 5 条 + 清空确认）；四模块生成成功后自动记录；彩排室第 3 轮记一条
- 产品意义：从"用一次的 Demo"到"有回访价值的产品"，评委二次打开能看到使用痕迹
| 模块 | 后端 | 前端 | 状态 |
|---|---|---|---|
| 关心解码器 | `POST /api/decode` | `DecodeView.vue` | ✅ |
| 回音壁 | `POST /api/reply` | `ReplyView.vue` | ✅ |
| 连心话题卡 | `POST /api/topic` | `TopicView.vue` | ✅ |
| 高难对话彩排室 | `/api/rehearsal/*` ×3 | `RehearsalView.vue` | ✅ |
| 三模块联通 | — | 路由跳转 + 预填 | ✅ |

无 API Key 全功能可跑（演示剧本兜底）；拿到 Key 填 `backend/.env` 即平滑切换真实大模型。
