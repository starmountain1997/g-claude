# Hermes 性能分析平台 - Docker 构建文件
# docker build -t hermes-backend .

FROM python:3.13-slim

LABEL maintainer="hermes-team"
LABEL version="v3.0"
LABEL description="Hermes 性能分析平台 (Gradio + LangGraph)"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p uploads

EXPOSE 8082

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/app.py"]
