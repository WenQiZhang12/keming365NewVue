# -*- coding: utf-8 -*-
"apps.admin_panel.views - 管理后台 视图"

from .admin import (
    CourseManageViewSet,
    DashboardView,
    ExperimentManageViewSet,
    NewsManageViewSet,
    SchoolManageViewSet,
    UserManageViewSet,
    ViewpagerManageViewSet,
)

__all__ = [
    'UserManageViewSet',
    'CourseManageViewSet',
    'ExperimentManageViewSet',
    'SchoolManageViewSet',
    'ViewpagerManageViewSet',
    'NewsManageViewSet',
    'DashboardView',
]
