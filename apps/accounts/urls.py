# -*- coding: utf-8 -*-
"""
apps.accounts.urls - 用户与账户 路由

路由前缀（在 config/urls.py 中定义）：/api/v1/accounts/
"""

from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views.auth import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    RegisterView,
    SendSmsView,
)
from apps.accounts.views.profile import (
    ChangePasswordView,
    ProfileView,
)

app_name = 'accounts'

urlpatterns = [
    # --- 认证 ---
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('auth/send-sms/', SendSmsView.as_view(), name='send_sms'),

    # --- 个人信息 ---
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
