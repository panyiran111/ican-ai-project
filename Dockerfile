# 家音后端 · Docker 镜像（Koyeb 等平台通用）
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用 Docker 层缓存）
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷贝代码
COPY backend/ .

ENV PYTHONUNBUFFERED=1

# Koyeb/Docker 平台会注入 PORT 环境变量，默认 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]