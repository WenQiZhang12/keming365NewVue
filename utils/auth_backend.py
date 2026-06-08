# -*- coding: utf-8 -*-
"""
自定义 JWT 认证后端

SimpleJWT 默认使用 Django 内置 User 模型查询用户。
TbUser 是 legacy `managed=False` 表，id 为 CharField (UUID 字符串)，
且不是 AbstractBaseUser 子类。

此认证后端覆写 `get_user` 方法，直接查询 TbUser 表。
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.accounts.models import TbUser


class TbUserJWTAuthentication(JWTAuthentication):
    """
    使用 TbUser 模型的 JWT 认证

    与标准 SimpleJWT 认证的唯一区别是 `get_user` 方法从 TbUser 表查询，
    而不是从 django.contrib.auth.models.User 查询。
    """

    def authenticate(self, request):
        """
        覆写 authenticate，自己处理认证流程。
        直接接管：
        1. 从 header 提取 token
        2. 验证 token
        3. 从 TbUser 表查用户
        """
        try:
            header = self.get_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)

            return self.get_user(validated_token), validated_token
        except Exception:
            return None

    def get_user(self, validated_token):
        """
        覆写 get_user，从 TbUser 表按 user_id 查询
        """
        user_id = validated_token.get('user_id')
        if not user_id:
            return None

        try:
            return TbUser.objects.get(id=user_id)
        except TbUser.DoesNotExist:
            return None
