# 科明365 教学云平台 — 部署指南

## 环境要求

- Docker & Docker Compose
- 域名（生产环境） + SSL 证书

## 快速部署

### 1. 克隆代码

```bash
git clone <repo-url> keming365-backend
cd keming365-backend
```

### 2. 配置环境变量

```bash
cp .env.prod.example .env
# 编辑 .env 填入实际的密钥、数据库密码、域名等
```

### 3. 准备 SSL 证书

将证书放入 `ssl/` 目录：

```
ssl/
├── fullchain.pem
└── privkey.pem
```

开发测试可用自签名证书，或先用 HTTP（修改 nginx.conf 去掉 HTTPS 重定向）。

### 4. 初始化数据库

将 SQL 文件放入 `scripts/init.sql`，容器首次启动会自动导入。

### 5. 启动所有服务

```bash
docker-compose up -d
```

### 6. 收集静态文件（首次部署）

```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

### 7. 创建管理员（首次部署）

```bash
docker-compose exec backend python manage.py shell -c "
from apps.accounts.models import TbUser
from django.utils import timezone
import uuid
TbUser.objects.create(
    id=uuid.uuid4().hex[:32],
    username='admin',
    password='pbkdf2_sha256\$...',  # 使用 createsuperuser 命令替代
    name='管理员',
    type=2
)
"
```

> 建议用 Django `manage.py shell` 交互式创建。

## 访问

| 服务 | 地址 |
|------|------|
| 前台首页 | https://keming365.com/ |
| 管理后台 | https://keming365.com/media/admin.html |
| API 文档 | https://keming365.com/api/docs/ |

## 常用命令

```bash
# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 更新代码后重新构建
docker-compose build backend
docker-compose up -d

# 备份数据库
docker-compose exec mysql mysqldump -u root -p new365 > backup.sql

# 进入 Django shell
docker-compose exec backend python manage.py shell
```

## 架构

```
┌─────────┐   ┌─────────┐   ┌──────────┐
│  Nginx  │──▶│ Gunicorn│──▶│ Django   │
│ (80/443)│   │ (8000)  │   │ (App)    │
└─────────┘   └─────────┘   └────┬─────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  MySQL   │ │  Redis   │ │  Media   │
              │  8.0     │ │  7       │ │  Files   │
              └──────────┘ └──────────┘ └──────────┘
```

## 注意事项

1. **Secret Key**: 生产环境务必通过环境变量设置强密钥
2. **HTTPS**: 生产环境必须启用 HTTPS
3. **数据库备份**: 定期备份 MySQL 数据
4. **文件存储**: 媒体文件存储在 Docker volume 中，建议挂载到 NAS 或云存储
5. **水平扩展**: 可启动多个 backend 实例，Nginx 负责负载均衡
