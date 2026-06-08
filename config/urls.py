# -*- coding: utf-8 -*-
"""
config.urls - 项目根 URL 配置

路由映射：
  admin/     → Django 管理后台
  api/v1/    → 各 App 路由（预留，按需注册）
  api/docs/  → Swagger 文档
  ws/        → WebSocket 路由（预留，按需注册）
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# ============================================================================
# URL 模式
# ============================================================================

urlpatterns = [
    # Django 管理后台
    path('admin/', admin.site.urls),

    # API 文档
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),

    # API v1 - 各 App 路由预留
    # 格式：path('api/v1/<app>/', include('apps.<app>.urls'))
    path('api/v1/', include([
        path('accounts/', include('apps.accounts.urls')),
        path('courses/', include('apps.courses.urls')),
        path('quizzes/', include('apps.quizzes.urls')),
        path('scores/', include('apps.scores.urls')),
        path('comments/', include('apps.comments.urls')),
        path('files/', include('apps.files.urls')),
        path('payments/', include('apps.payments.urls')),
        path('notifications/', include('apps.notifications.urls')),
        path('news/', include('apps.news.urls')),
        path('home/', include('apps.home.urls')),
        path('admin/', include('apps.admin_panel.urls')),
        path('assessment/', include('apps.assessment.urls')),
        # path('common/', include('apps.common.urls')),
    ])),
]

# ============================================================================
# 开发模式额外路由
# ============================================================================

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
