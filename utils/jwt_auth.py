# -*- coding: utf-8 -*-
"""自定义 JWT 认证后端 - 使用 tb_user 表"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.models import TokenUser


class TbUserJWTAuthentication(JWTAuthentication):
    """使用 TokenUser 替代数据库查询"""

    def get_user(self, validated_token):
        """
        返回 TokenUser 而不是查询 tb_user 表。
        TokenUser 包含 id 字段。
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contains no recognizable user identification')

        user = TokenUser(validated_token)
        # 添加 type 属性，供 IsAdminUser 权限检查使用
        if hasattr(user, 'id'):
            # 延迟加载 type 字段
            from apps.accounts.models import TbUser
            try:
                tb_user = TbUser.objects.only('type').get(id=user_id)
                user.type = tb_user.type
            except TbUser.DoesNotExist:
                user.type = 0
        return user
