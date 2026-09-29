# Render 部署说明（后端 FastAPI）

## 项目结构
- 仓库根目录：`C:\Users\潘亦然\Desktop\家音.潘\`
- 后端代码：`backend/`
- 配置文件：`render.yaml`（仓库根目录）

## Render 控制台配置（Web 端点点点）

### 方式 A：用 Blueprint（推荐，已经配好 render.yaml）
1. 登录 https://render.com
2. New + → Blueprint
3. 连 GitHub → 选你的仓库 → Apply
4. Render 自动读 `render.yaml` 建服务
5. 等 5-10 分钟 → 拿到 `xxx.onrender.com`

### 方式 B：手动建 Web Service
1. New + → Web Service
2. 连 GitHub → 选仓库
3. 配置：
   - **Root Directory**：`backend`
   - **Runtime**：`Python 3`
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**：`Free`（0元/月）
   - **Health Check Path**：`/api/health`

### 环境变量（可选，不填也能跑）
在 Environment 里：
| Key | Value |
| --- | --- |
| `LLM_API_KEY` | 你的大模型 Key（不填走演示剧本，永不翻车） |
| `LLM_BASE_URL` | `https://api.deepseek.com` |
| `LLM_MODEL` | `deepseek-chat` |
| `PYTHON_VERSION` | `3.11.9` |

## 健康检查
- URL：`https://你的服务.onrender.com/api/health`
- 返回：`{"status":"ok","service":"jiayin","llm_ready":false}`
- 首次冷启动 30-60s，请稍候

## 故障排查

| 问题 | 原因 | 解决 |
|---|---|---|
| Build failed: `ModuleNotFoundError` | requirements.txt 没装全 | 检查 backend/requirements.txt |
| Start failed: `Address already in use` | $PORT 没注入 | 命令改成 `--port $PORT`（已配好） |
| 502 Bad Gateway | 冷启动中 | 等 30-60s 再刷新 |
| 启动后立即挂掉 | rootDir 选错 | 改成 `backend` |
| API Key 报错 401 | Key 过期或 Base URL 错 | 检查环境变量 |

## 免费版注意事项
- 15 分钟无请求会休眠 → 下次冷启动 30-60s
- 750 小时/月免费额度 → 比赛期间完全够用
- 数据库无状态（演示用），重启不丢数据

## 自动部署
- push 到 main 分支 → Render 自动重新部署
- 可在 Render 控制台开启 Auto-Deploy