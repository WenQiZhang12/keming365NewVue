# -*- coding: utf-8 -*-
"""
apps.files.urls - 文件管理 路由

路由前缀：/api/v1/files/
"""

from django.urls import path

from apps.files.views.files import (
    FilePreviewView,
    FileUploadView,
    VideoDetailView,
    VideoListView,
    experiment_report,
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('report/<str:experiment_id>/', experiment_report, name='experiment_report'),
    path('preview/<path:file_path>/', FilePreviewView.as_view(), name='file_preview'),
    path('videos/', VideoListView.as_view(), name='video_list'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
]
