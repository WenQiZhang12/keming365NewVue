# -*- coding: utf-8 -*-
"""
ASGI config for keming365 project.

支持 Django Channels (WebSocket) 和传统的 HTTP 请求。
用于 Uvicorn / Daphne 等 ASGI 服务器。
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 初始化 Django ASGI 应用（尽早，确保 apps 已加载）
django_asgi_app = get_asgi_application()

# WebSocket 路由 - 从 apps 导入
from apps.notifications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP 请求交给 Django 处理
    'http': django_asgi_app,
    # WebSocket 请求交给 Channels 路由
    'websocket': URLRouter(websocket_urlpatterns),
})
