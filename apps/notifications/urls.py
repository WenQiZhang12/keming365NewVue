# -*- coding: utf-8 -*-
"""
apps.notifications.urls - 消息通知 路由

路由前缀（在 config/urls.py 中定义）：/api/v1/notifications/
"""

from django.urls import path

from apps.notifications.views.notifications import SendSmsView

app_name = 'notifications'

urlpatterns = [
    # --- 短信 ---
    path('send-sms/', SendSmsView.as_view(), name='send_sms'),
]
