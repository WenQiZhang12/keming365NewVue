# 生产部署检查清单

## 上线前必须改回的地方

### 1. nginx.conf — 恢复 HTTPS
上线前把当前 HTTP 配置替换回 HTTPS 配置（ssl/目录放证书）：

- `listen 8080;` → `listen 443 ssl http2;` + 再加一道 `listen 80; return 301 https://...`
- `server_name localhost` → 改成实际域名
- 加回 SSL 证书相关配置（`ssl_certificate`, `ssl_certificate_key` 等）
- 加回安全头（HSTS, X-Frame-Options 等）

### 2. config/settings/prod.py — 恢复安全配置
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# 上面三项在当前 prod.py 中已被改为 False，上线时改回 True
```

### 3. 环境变量（docker-compose.yml 或 .env）
- `DJANGO_SECRET_KEY`：替换 `dev-deploy-key-2024` 为真实密钥
- `DJANGO_ALLOWED_HOSTS`：加上实际域名
- `CORS_ALLOWED_ORIGINS`：加上实际前端域名
- `DB_PASSWORD`：改为强密码

### 4. docker-compose.yml
```yaml
ports:
  - "8080:80"   → 改回 "80:80" 和 "443:443"
```

### 5. 初始化数据库
第一次部署需要初始化 MySQL 数据（当前 sqlite 的数据不通用）：
```bash
# 先确认 scripts/init.sql 存在且包含表结构和初始数据
# 容器启动后如有必要可执行：
docker exec -i keming365-mysql mysql -uroot -p new365 < scripts/init.sql
```
