# 家音 Jiayin · AI 家庭沟通翻译官

> 爸妈的每一条养生文，都是没说出口的想你。
> 2026 iCAN 大学生创新创业大赛 · 快手·AI未来创造者挑战赛 · 9月月赛「我们与AI」· AI产品实现方向

「家音」站在父母与子女之间：把父母的"关心式轰炸"翻译成子女听得懂的语言，把子女的"沉默式在意"翻译成父母读得懂的表达。

## 功能
- **家音小助手**：首页迷你小人挥手打招呼（纯 CSS 动画），支持「我是爸妈 / 我是你」双角色——爸妈打开收到热情问候，还会播报真实动态（今天打卡了吗、合养的宠物长大没），点一下换一句 ✅
- **关心解码器**：60秒语音/养生文 → 核心信息压缩 + 情感意图解码（不辟谣打脸，只翻译爱）✅
- **回音壁**：三档温度回复生成，像你本人说的话（嘴硬/标准/撒娇，一键复制）✅
- **高难对话彩排室**：AI 扮演爸妈多轮对话，先心疼再问情况，彩排挂科/分手/辞职/要生活费等难开口话题，练顺了再打真电话 ✅
- **连心话题卡**：回家前/节日/生日/普通通话 4 场景，各抽 5 个不尬聊的开放式话题 ✅
- **三模块联通**：解码结果一键跳回音壁生成回复 → 复制后一键去彩排室练习 ✅
- **我家小档案**：填一次爸妈称呼/老家/拿手菜/爱好，生成内容自动带上你家的味道（localStorage，不上传）✅
- **最近的家音**：解码/回复/话题/彩排记录自动留痕，二次打开可回看 ✅
- **语音能力**：对着麦克风说就能输入（不用打字），生成的回复可一键朗读试听（Chrome/Edge）✅
- **每日安心打卡**：拍一张今天的生活 + 一句话，连续天数解锁徽章（3/7/21/50/90 天），安心值可视化，断签不惩罚 ✅
- **今日卡 + 老家天气**：日期 + 节日倒计时（制造通话契机）；老家实时天气（Open-Meteo 无 Key）+ 现成的关心建议，一键跳回音壁生成「天气问候」✅
- **合养小宠物**：全家的孩子——完成沟通任务赚成长值（解码+5/回音+5/话题+3/彩排+10/打卡+10），四阶段成长 + 每日喂食 + 一键生成「宠物近况」分享给爸妈，断喂不惩罚 ✅

## 目录结构
```
backend/
├── main.py           # FastAPI 入口：/api/decode /api/reply /api/topic /api/rehearsal/*
├── llm.py            # 提示词 + 演示剧本引擎（10 场景解码/三档回复/4 场景话题卡/4 场景彩排剧本）
├── test_rehearsal.py # 彩排室回归测试
└── requirements.txt
frontend/
└── src/views/        # Home / Decode / Reply / Topic / Rehearsal（Hash 路由 + 底部 Tab）
```

## 本地启动（三步）
```bash
# 1. 后端
cd backend
pip install -r requirements.txt
copy .env.example .env   # 填入 LLM_API_KEY（不填也可跑，自动降级演示数据）
uvicorn main:app --reload --port 8000

# 2. 前端（新开终端）
cd frontend
npm install
npm run dev              # http://localhost:5173
```

## 在线体验
- 前端（Vercel）：https://____.vercel.app （D3 部署后填写，详见 `DEPLOY_STEPS.md`）
- 后端 API（Render）：https://____.onrender.com （D3 部署后填写，详见 `DEPLOY_STEPS.md`）
- 应急临时公网链接：双击 `emergency-demo.bat` → 1 分钟内生成 `https://xxx.trycloudflare.com`

> 后端无 API Key 也能跑（自动降级内置演示剧本），Render 免费版冷启动约 30-60 秒，首次打开请稍候。

## 部署说明
- 后端：仓库根目录 `render.yaml`（Render Blueprint，rootDir=backend，`uvicorn main:app --port $PORT`）
- 前端：根目录 `vercel.json` + Vercel 导入同一仓库，Root Directory 选 `frontend`，在控制台添加环境变量 `VITE_API_BASE=<Render 后端地址>`
- 本地开发：`frontend/.env.development` 留空即可（走 Vite 代理到 127.0.0.1:8000）
- **零基础完整操作手册**：[`DEPLOY_STEPS.md`](./DEPLOY_STEPS.md) ← 推荐首次操作者看这个
- **精简版操作手册**：[`DEPLOY_NOW.md`](./DEPLOY_NOW.md)
- **一键推送脚本**：双击 `push-to-github.bat`（会引导填用户名/邮箱/仓库名）
- 详细说明：[`docs/RENDER_DEPLOY.md`](./docs/RENDER_DEPLOY.md) / [`docs/VERCEL_DEPLOY.md`](./docs/VERCEL_DEPLOY.md)

## 演示剧本
无 API Key 时，全部模块自动降级为内置演示数据（解码 10 场景 / 回音壁 10 场景 × 3 档 / 话题卡 4 场景 × 5 题 / 彩排室 4 场景 × 5 轮），保证演示永不翻车。

## API 一览
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/decode` | 关心解码器（两段式：压缩 + 情感） |
| POST | `/api/reply` | 回音壁（tough/normal/sweet 三档） |
| POST | `/api/topic` | 话题卡（4 场景 × 5 问题） |
| GET | `/api/topic/scenes` | 话题卡场景列表 |
| POST | `/api/rehearsal/start` | 彩排室：创建会话 + 爸妈开场白 |
| POST | `/api/rehearsal/chat` | 彩排室：多轮对话 |
| GET | `/api/rehearsal/scenes` | 彩排室场景列表 |
| GET | `/api/weather` | 老家天气（Open-Meteo，无 Key，失败降级示例数据） |
