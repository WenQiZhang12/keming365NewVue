# -*- coding: utf-8 -*-
"""
Django 生产环境配置

DEBUG 关闭，启用 HTTPS，限制 ALLOWED_HOSTS。
"""

from .base import *  # noqa: F401, F403

# ============================================================================
# 调试
# ============================================================================

DEBUG = False

# ============================================================================
# 主机白名单 - 从环境变量读取，多个用逗号分隔
# ============================================================================

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1',
).split(',')

# ============================================================================
# HTTPS 安全配置
# ============================================================================

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 31536000  # 1 年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ============================================================================
# CORS - 从环境变量读取允许的域名
# ============================================================================

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    '',
).split(',')

# ============================================================================
# 静态文件 - 生产环境建议用 CDN/Nginx
# ============================================================================

# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# ============================================================================
# Email - 生产环境使用 SMTP
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@keming365.com')
