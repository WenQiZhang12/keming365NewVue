# -*- coding: utf-8 -*-
"""
apps.courses.views.chapter - 章节 视图

所有章节接口允许匿名访问。
"""

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.courses.models import Chapter
from apps.courses.serializers import ChapterTreeSerializer


class ChapterTreeView(ListAPIView):
    """
    GET /api/v1/courses/<curriculum_id>/chapters/

    获取课程的章节树（按 order 排序，含知识节点）
    """
    serializer_class = ChapterTreeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        curriculum_id = self.kwargs.get('curriculum_id')
        return Chapter.objects.filter(
            curriculumId=curriculum_id
        ).order_by('order')


class ChapterDetailView(RetrieveAPIView):
    """
    GET /api/v1/chapters/<id>/

    获取章节详情
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterTreeSerializer
    permission_classes = [AllowAny]
