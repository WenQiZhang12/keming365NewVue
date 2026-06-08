# -*- coding: utf-8 -*-
"""
apps.courses.views.curriculum - 课程 视图

所有课程列表/详情接口允许匿名访问。
"""

from django.db.models import Count
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.courses.models import TbCurriculum
from apps.courses.serializers import (
    CurriculumDetailSerializer,
    CurriculumListSerializer,
)
from utils.pagination import StandardPagination


class CurriculumListView(ListAPIView):
    """
    GET /api/v1/courses/

    课程列表

    查询参数：
      classifyId - 分类 ID（可选，按分类过滤）
      page       - 页码（默认 1）
      page_size  - 每页数量（默认 20，最大 100）
    """
    queryset = TbCurriculum.objects.all().order_by('sortOrder', '-createTime')
    serializer_class = CurriculumListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        classify_id = self.request.query_params.get('classifyId')
        if classify_id:
            qs = qs.filter(classifyId=classify_id)
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(curriculumName__icontains=search)
        return qs


class CurriculumDetailView(RetrieveAPIView):
    """
    GET /api/v1/courses/<id>/

    课程详情（含实验列表和章节树）
    """
    queryset = TbCurriculum.objects.all()
    serializer_class = CurriculumDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
