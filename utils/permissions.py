# -*- coding: utf-8 -*-
"""
utils.permissions - 自定义权限类

权限体系基于用户 type 字段：
  type=0 → 普通用户（学生）
  type=1 → 教师
  type=2 → 管理员
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    """
    仅管理员（type=2）可访问
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'type', None) == 2
        )


class IsTeacherOrAdmin(BasePermission):
    """
    教师（type=1）或管理员（type=2）可访问
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_type = getattr(request.user, 'type', None)
        return user_type in (1, 2)


class IsOwnerOrAdmin(BasePermission):
    """
    对象所有者或管理员可访问

    用于资源级别的权限控制，需要模型有 user / owner 字段，
    view 中有 get_owner_field 方法或默认使用 'user' 字段。

    使用示例:
      class MyView(GenericAPIView):
          permission_classes = [IsOwnerOrAdmin]

          def get_owner_field(self):
              return 'user'  # 默认

          def get_queryset(self):
              # 查询时自动过滤
              return Model.objects.filter(user=self.request.user)
    """

    def has_object_permission(self, request, view, obj):
        # 管理员拥有所有权限
        if getattr(request.user, 'type', None) == 2:
            return True

        # 检查是否为对象所有者
        owner_field = getattr(view, 'get_owner_field', lambda: 'user')()
        owner = getattr(obj, owner_field, None)
        return owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    """
    所有者可写，其他用户只读

    适合评论、个人资料等场景。
    """

    def has_object_permission(self, request, view, obj):
        # 安全方法（GET、HEAD、OPTIONS）允许所有用户
        if request.method in SAFE_METHODS:
            return True

        # 写操作仅允许所有者
        owner_field = getattr(view, 'get_owner_field', lambda: 'user')()
        owner = getattr(obj, owner_field, None)
        return owner == request.user
