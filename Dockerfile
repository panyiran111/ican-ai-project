# 家音后端 · Docker 镜像（Railway/Koyeb 等平台通用）
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

ENV PYTHONUNBUFFERED=1

# 端口固定 8000（Railway 域名 target port 已设为 8000）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]
