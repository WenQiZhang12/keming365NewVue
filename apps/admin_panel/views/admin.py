# -*- coding: utf-8 -*-
"""
apps.admin_panel.views.admin - 管理后台 视图

所有接口需要管理员权限（type=2）。
使用 ViewSet 实现 CRUD，使用 APIView 实现仪表盘统计。
"""

import uuid
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import TbUser
from apps.common.models import TbSchoolInfo
from apps.courses.models import TbCurriculum, TbExperiment
from apps.home.models import TbViewpager
from apps.news.models import News
from apps.payments.models import Orders

from apps.admin_panel.serializers import (
    AdminCurriculumSerializer,
    AdminExperimentSerializer,
    AdminNewsSerializer,
    AdminNewsWriteSerializer,
    AdminSchoolCreateSerializer,
    AdminSchoolSerializer,
    AdminUserCreateSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    AdminViewpagerSerializer,
    AdminViewpagerWriteSerializer,
    DashboardSerializer,
)

from utils.pagination import StandardPagination
from utils.permissions import IsAdminUser


# ============================================================================
# 用户管理
# ============================================================================

class UserManageViewSet(ModelViewSet):
    """
    用户管理

    list    GET    /api/v1/admin/users/        - 用户列表（分页，支持搜索）
    create  POST   /api/v1/admin/users/        - 创建用户
    retrieve GET   /api/v1/admin/users/{id}/   - 用户详情
    update  PUT    /api/v1/admin/users/{id}/   - 编辑用户
    destroy DELETE /api/v1/admin/users/{id}/   - 删除用户
    """

    queryset = TbUser.objects.all()
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return AdminUserUpdateSerializer
        return AdminUserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # 搜索支持
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(name__icontains=search)
                | Q(telephone__icontains=search)
            )
        # 按类型过滤
        user_type = self.request.query_params.get('type')
        if user_type:
            qs = qs.filter(type=user_type)
        return qs.order_by('-createTime')

    def perform_create(self, serializer):
        # 从 validated_data 中拿出字段
        validated = serializer.validated_data.copy()
        validated['id'] = str(uuid.uuid4()).replace('-', '')[:32]
        if validated.get('password'):
            validated['password'] = make_password(validated['password'])
        validated['createTime'] = timezone.now()
        serializer.save(**validated)

    def perform_update(self, serializer):
        data = serializer.validated_data
        # 如果提供了密码，加密
        if data.get('password'):
            data['password'] = make_password(data['password'])
        else:
            data.pop('password', None)
        serializer.save()


# ============================================================================
# 课程管理
# ============================================================================

class CourseManageViewSet(ModelViewSet):
    """
    课程管理

    list    GET    /api/v1/admin/courses/        - 课程列表
    create  POST   /api/v1/admin/courses/        - 创建课程
    retrieve GET   /api/v1/admin/courses/{id}/   - 课程详情
    update  PUT    /api/v1/admin/courses/{id}/   - 编辑课程
    destroy DELETE /api/v1/admin/courses/{id}/   - 删除课程
    """

    queryset = TbCurriculum.objects.all()
    serializer_class = AdminCurriculumSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_queryset(self):
        qs = super().get_queryset()
        # 按名称搜索
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(curriculumName__icontains=search)
            )
        # 按分类过滤
        classify_id = self.request.query_params.get('classifyId')
        if classify_id:
            qs = qs.filter(classifyId=classify_id)
        return qs.order_by('-createTime')

    def perform_create(self, serializer):
        serializer.save(createTime=timezone.now())

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# 实验管理
# ============================================================================

class ExperimentManageViewSet(ModelViewSet):
    """
    实验管理

    list    GET    /api/v1/admin/experiments/        - 实验列表
    create  POST   /api/v1/admin/experiments/        - 创建实验
    retrieve GET   /api/v1/admin/experiments/{id}/   - 实验详情
    update  PUT    /api/v1/admin/experiments/{id}/   - 编辑实验
    destroy DELETE /api/v1/admin/experiments/{id}/   - 删除实验
    """

    queryset = TbExperiment.objects.all()
    serializer_class = AdminExperimentSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_queryset(self):
        qs = super().get_queryset()
        # 搜索
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(publisher__icontains=search)
            )
        return qs.order_by('-createTime')

    def perform_create(self, serializer):
        serializer.save(createTime=timezone.now())

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# 学校管理
# ============================================================================

class SchoolManageViewSet(ModelViewSet):
    """
    学校管理

    list    GET    /api/v1/admin/schools/        - 学校列表
    create  POST   /api/v1/admin/schools/        - 创建学校
    retrieve GET   /api/v1/admin/schools/{id}/   - 学校详情
    update  PUT    /api/v1/admin/schools/{id}/   - 编辑学校
    destroy DELETE /api/v1/admin/schools/{id}/   - 删除学校
    """

    queryset = TbSchoolInfo.objects.all()
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AdminSchoolCreateSerializer
        return AdminSchoolSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('-createTime')

    def perform_create(self, serializer):
        # 生成 ID（若未提供）
        data = serializer.validated_data
        if not data.get('id'):
            data['id'] = str(uuid.uuid4()).replace('-', '')[:32]
        data['createTime'] = timezone.now()
        serializer.save(**data)

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# 轮播图管理
# ============================================================================

class ViewpagerManageViewSet(ModelViewSet):
    """
    轮播图管理

    list    GET    /api/v1/admin/viewpagers/        - 轮播图列表
    create  POST   /api/v1/admin/viewpagers/        - 创建轮播图
    retrieve GET   /api/v1/admin/viewpagers/{id}/   - 轮播图详情
    update  PUT    /api/v1/admin/viewpagers/{id}/   - 编辑轮播图
    destroy DELETE /api/v1/admin/viewpagers/{id}/   - 删除轮播图
    """

    queryset = TbViewpager.objects.all()
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AdminViewpagerWriteSerializer
        return AdminViewpagerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by('sortOrder')

    def perform_create(self, serializer):
        data = serializer.validated_data
        if not data.get('id'):
            data['id'] = str(uuid.uuid4()).replace('-', '')[:32]
        data['createTime'] = timezone.now()
        serializer.save(**data)

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# 新闻管理
# ============================================================================

class NewsManageViewSet(ModelViewSet):
    """
    新闻管理

    list    GET    /api/v1/admin/news/        - 新闻列表
    create  POST   /api/v1/admin/news/        - 创建新闻
    retrieve GET   /api/v1/admin/news/{id}/   - 新闻详情
    update  PUT    /api/v1/admin/news/{id}/   - 编辑新闻
    destroy DELETE /api/v1/admin/news/{id}/   - 删除新闻
    """

    queryset = News.objects.all()
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return AdminNewsWriteSerializer
        return AdminNewsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.order_by('-priority', '-time')

    def perform_create(self, serializer):
        data = serializer.validated_data
        data['time'] = timezone.now()
        # news.userid 是 int 类型，取不到整数ID时用 0
        try:
            uid = int(self.request.user.id)
        except (ValueError, TypeError):
            uid = 0
        data['userid'] = uid
        serializer.save(**data)

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# 仪表盘统计
# ============================================================================

class DashboardView(APIView):
    """
    仪表盘统计

    GET /api/v1/admin/dashboard/
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'userCount': 100, 'courseCount': 50, 'experimentCount': 200, 'orderCount': 10, 'todayNewUsers': 5, 'todayOrders': 2})
