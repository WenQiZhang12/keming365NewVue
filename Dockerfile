# ============================================================================
# Dockerfile — 科明365 教学云平台 生产镜像
# ============================================================================
# 多阶段构建：builder → runtime

# ---- 构建阶段 ----
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装编译依赖（mysqlclient 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 拷贝 requirements
COPY requirements/base.txt requirements/base.txt

# 安装 Python 依赖到 /install 目录
RUN pip install --no-cache-dir --prefix=/install -r requirements/base.txt

# ---- 运行阶段 ----
FROM python:3.11-slim

WORKDIR /app

# 仅安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制已安装的 Python 包
COPY --from=builder /install /usr/local

# 拷贝项目代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --settings=config.settings.prod --noinput

# 暴露端口
EXPOSE 8000

# 使用 gunicorn 启动
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
