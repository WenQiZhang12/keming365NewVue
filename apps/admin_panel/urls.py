# -*- coding: utf-8 -*-
"""
apps.admin_panel.urls - 管理后台 路由

路由前缀（在 config/urls.py 中定义）：/api/v1/admin/
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from apps.admin_panel.views import (
    CourseManageViewSet,
    DashboardView,
    ExperimentManageViewSet,
    NewsManageViewSet,
    SchoolManageViewSet,
    UserManageViewSet,
    ViewpagerManageViewSet,
)

# ============================================================================
# 使用 DefaultRouter 自动注册 ViewSet 路由
# ============================================================================

router = DefaultRouter()
router.register(r'users', UserManageViewSet, basename='admin-user')
router.register(r'courses', CourseManageViewSet, basename='admin-course')
router.register(r'experiments', ExperimentManageViewSet, basename='admin-experiment')
router.register(r'schools', SchoolManageViewSet, basename='admin-school')
router.register(r'viewpagers', ViewpagerManageViewSet, basename='admin-viewpager')
router.register(r'news', NewsManageViewSet, basename='admin-news')

urlpatterns = [
    # 仪表盘统计（APIView，手动注册）
    path('dashboard/', DashboardView.as_view(), name='admin-dashboard'),

    # ViewSet 自动路由（自动生成 list / create / retrieve / update / destroy）
    path('', include(router.urls)),
]
