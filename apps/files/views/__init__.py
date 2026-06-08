# -*- coding: utf-8 -*-
"""
apps.files.views - 文件管理 视图
"""

from apps.files.views.files import FilePreviewView, FileUploadView, VideoDetailView, VideoListView, experiment_report

__all__ = [
    'FileUploadView',
    'FilePreviewView',
    'VideoListView',
    'VideoDetailView',
    'experiment_report',
]
