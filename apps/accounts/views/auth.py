# -*- coding: utf-8 -*-
"""
apps.accounts.views.auth - 认证相关视图

提供注册、登录、登出、刷新 Token 等接口
"""

import logging

from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from apps.accounts.models import TbUser
from apps.accounts.serializers import (
    SendSmsSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)
from utils.exceptions import BusinessError

logger = logging.getLogger(__name__)


# ============================================================================
# 注册
# ============================================================================

class RegisterView(APIView):
    """用户注册

    POST /api/v1/accounts/auth/register/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'type': user.type or 0,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================================
# 登录
# ============================================================================

class LoginView(APIView):
    """用户登录

    POST /api/v1/accounts/auth/login/
    返回 JWT Token 和用户基本信息
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成 JWT Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'type': user.type or 0,
                },
            },
            status=status.HTTP_200_OK,
        )


# ============================================================================
# 登出
# ============================================================================

class LogoutView(APIView):
    """用户登出（黑名单 Token）

    POST /api/v1/accounts/auth/logout/
    需要认证（提供有效的 access token）
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            logger.warning(f'Logout blacklist error: {e}')
            # 即使黑名单失败，登出操作仍然成功
            pass

        return Response(
            {'message': '登出成功'},
            status=status.HTTP_200_OK,
        )


# ============================================================================
# 刷新 Token
# ============================================================================

class RefreshTokenView(BaseTokenRefreshView):
    """刷新 Token

    POST /api/v1/accounts/auth/refresh/
    允许匿名访问（通过 refresh token 换取新的 access token）
    """

    permission_classes = [AllowAny]


# ============================================================================
# 发送短信验证码
# ============================================================================

class SendSmsView(APIView):
    """发送短信验证码

    POST /api/v1/accounts/auth/send-sms/
    允许匿名
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 验证码已通过序列化器发送
        return Response(
            {'message': '验证码已发送', 'telephone': serializer.validated_data['telephone']},
            status=status.HTTP_200_OK,
        )
