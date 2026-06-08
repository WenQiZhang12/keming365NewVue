# -*- coding: utf-8 -*-
"""
Django 5.x 公共配置文件

包含 Django、DRF、JWT、数据库、缓存、CORS、
静态/媒体文件、API 文档、WebSocket 等所有公共配置。
敏感信息通过环境变量或 .env 文件读取。
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# ============================================================================
# 路径与基础
# ============================================================================

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================================================
# 安全密钥
# ============================================================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    # 默认值仅用于开发，生产环境务必通过环境变量覆盖
    'django-insecure-default-dev-key-change-in-production',
)

# ============================================================================
# 调试与主机
# ============================================================================

DEBUG = False  # 子配置文件覆盖

ALLOWED_HOSTS: list[str] = []  # 子配置文件覆盖

# ============================================================================
# 应用注册
# ============================================================================

INSTALLED_APPS = [
    # Django 内置
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'channels',

    # 项目 App
    'apps.accounts',
    'apps.courses',
    'apps.quizzes',
    'apps.scores',
    'apps.comments',
    'apps.files',
    'apps.payments',
    'apps.notifications',
    'apps.news',
    'apps.home',
    'apps.admin_panel',
    'apps.common',
]

# ============================================================================
# 中间件
# ============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # CORS - 需放在最外层
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# URL 与 WSGI/ASGI
# ============================================================================

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Channels 层使用 Redis
ASGI_APPLICATION = 'config.asgi.application'

# ============================================================================
# 模板
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================================
# 数据库 - MySQL
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'new365'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': (
                "SET sql_mode='STRICT_TRANS_TABLES', "
                "innodb_strict_mode=1"
            ),
        },
        'CONN_MAX_AGE': 600,  # 持久连接
    },
}

# ============================================================================
# 缓存 - Redis (django-redis)
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'keming365',
    },
}

# ============================================================================
# Channels 层配置 (Redis)
# ============================================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')],
        },
    },
}

# ============================================================================
# 密码验证
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# 用户模型
# 使用 custom managed=False 的 TbUser 表，不设置 AUTH_USER_MODEL
# JWT 认证通过自定义 Backend 处理
# ============================================================================

# AUTH_USER_MODEL = 'accounts.User'

# ============================================================================
# 国际化
# ============================================================================

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# ============================================================================
# 静态文件
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ============================================================================
# 媒体文件
# ============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# 默认主键
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CORS 配置 (django-cors-headers)
# ============================================================================

# 生产环境子配置覆盖为具体域名
CORS_ALLOWED_ORIGINS: list[str] = [
    # 子配置文件会覆盖此列表
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ============================================================================
# DRF 配置
# ============================================================================

REST_FRAMEWORK = {
    # 认证方案：优先 JWT，回退 Session
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'utils.auth_backend.TbUserJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

    # 权限：默认需认证，视图可按需开放
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # 分页：使用项目通用分页类
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardPagination',
    'PAGE_SIZE': 20,

    # 异常处理：统一返回格式
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',

    # 渲染器与解析器
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),

    # API 版本与限流
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',

    # dev 阶段关闭频率限制，生产环境再打开
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'rest_framework.throttling.UserRateThrottle',
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '100/hour',
    #     'user': '1000/hour',
    # },

    # OpenAPI 文档
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ============================================================================
# SimpleJWT 配置
# ============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'USER_ID_FIELD': 'id',
    # TbUser.id 是 CharField (UUID 字符串)，告知 SimpleJWT id 类型
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    # 自定义 get_user 函数 - 使用 TokenUser 替代从 auth_user 表查询
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=2),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# ============================================================================
# drf-spectacular 文档配置
# ============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Keming365 API',
    'DESCRIPTION': 'Keming365 在线教育平台后端 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    # 中文 Tag 翻译
    'TAGS': [
        {'name': 'accounts', 'description': '用户与账户'},
        {'name': 'courses', 'description': '课程管理'},
        {'name': 'quizzes', 'description': '测验与考试'},
        {'name': 'scores', 'description': '成绩管理'},
        {'name': 'comments', 'description': '评论与讨论'},
        {'name': 'files', 'description': '文件管理'},
        {'name': 'payments', 'description': '支付与订单'},
        {'name': 'notifications', 'description': '消息通知'},
        {'name': 'news', 'description': '新闻与公告'},
        {'name': 'home', 'description': '首页'},
        {'name': 'admin_panel', 'description': '管理后台'},
        {'name': 'common', 'description': '通用接口'},
    ],
}

# ============================================================================
# Celery 配置
# ============================================================================

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/2')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 分钟

# ============================================================================
# 日志
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[{levelname}] {asctime} {module} {process:d} {thread:d} '
                '{message}'
            ),
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # dev 会覆盖为 DEBUG
            'propagate': False,
        },
    },
}

# ============================================================================
# 云渲染平台配置 (YQCloud)
# 用于获取 Unity/3D 实验的运行 URL
# ============================================================================

YQ_CLOUD_CONFIGS = {
    'experiment': {
        'appKey': os.environ.get('YQ_APPKEY_EXPERIMENT', 'VUuNRF8L'),
        'appSecret': os.environ.get('YQ_APPSECRET_EXPERIMENT', 'e7ab133dda24473da613c8927269166b'),
    },
    'fragment': {
        'appKey': os.environ.get('YQ_APPKEY_FRAGMENT', 'Jx3wQMD1'),
        'appSecret': os.environ.get('YQ_APPSECRET_FRAGMENT', '6cdf1d37d5fb4d46a117b399c092cd24'),
    },
    'training': {
        'appKey': os.environ.get('YQ_APPKEY_TRAINING', 'DrcnSVZZ'),
        'appSecret': os.environ.get('YQ_APPSECRET_TRAINING', 'aadb5f80872c4f6286217b952781d559'),
    },
}

YQ_TOKEN_URL = os.environ.get('YQ_TOKEN_URL', 'http://58.56.66.170:8181')
YQ_SCORE_URL = os.environ.get('YQ_SCORE_URL', 'http://localhost:8000/api/v1/scores/report/')
YQ_USAGE_URL = os.environ.get('YQ_USAGE_URL', 'http://localhost:8000/api/v1/scores/usage/')
