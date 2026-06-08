# -*- coding: utf-8 -*-
"""
apps.notifications.routing - WebSocket 路由

注册 notifications App 的 WebSocket 消费者路由。
在 config/asgi.py 中通过 URLRouter 集成。
"""

from django.urls import re_path

from apps.notifications import consumers

websocket_urlpatterns = [
    # 实验实时推送 WebSocket
    # ws://host/ws/experiment/<experiment_id>/
    # 替换 Java 的 Pushlet，实现实验协作实时数据同步
    re_path(
        r'ws/experiment/(?P<experiment_id>\w+)/$',
        consumers.ExperimentConsumer.as_asgi(),
        name='experiment_ws',
    ),

    # 用户通知 WebSocket
    # ws://host/ws/notifications/<user_id>/
    # 向指定用户推送系统通知、评分通知等
    re_path(
        r'ws/notifications/(?P<user_id>\w+)/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notification_ws',
    ),
]
