# -*- coding: utf-8 -*-
"""
apps.courses.views.experiment - 实验 视图

所有实验列表/详情接口允许匿名访问。
"""

from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.courses.models import TbExperiment, TbCurriculum
from apps.courses.serializers import (
    ExperimentDetailSerializer,
    ExperimentListSerializer,
)
from utils.pagination import StandardPagination


class ExperimentListView(ListAPIView):
    """
    GET /api/v1/experiments/

    实验列表

    查询参数：
      curriculumId - 课程 ID（可选）
      chapterId    - 章节 ID（可选）
      search       - 搜索关键词（按标题模糊搜索）
      page         - 页码（默认 1）
      page_size    - 每页数量（默认 20，最大 100）
    """
    queryset = TbExperiment.objects.all().order_by('-createTime')
    serializer_class = ExperimentListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        qs = super().get_queryset()
        chapter_id = self.request.query_params.get('chapterId')
        if chapter_id:
            qs = qs.filter(chapterId=chapter_id)
        classify_id = self.request.query_params.get('classifyId')
        if classify_id:
            # classifyId 是 tb_classify.id，需要先查找该分类下的所有课程
            # 再通过课程的 id (parentId) 过滤实验
            curriculum_ids = TbCurriculum.objects.filter(
                classifyId=classify_id
            ).values_list('id', flat=True)
            qs = qs.filter(parentId__in=list(curriculum_ids))
        # 前端也可能传 curriculumId
        curriculum_id = self.request.query_params.get('curriculumId')
        if curriculum_id:
            qs = qs.filter(parentId=curriculum_id)
        # 按类型筛选：0=实验教学, 1=课堂教学, 3=教学模型
        exp_type = self.request.query_params.get('type')
        if exp_type is not None:
            qs = qs.filter(type=exp_type)
        return qs


class ExperimentDetailView(RetrieveAPIView):
    """
    GET /api/v1/experiments/<id>/

    实验详情
    """
    queryset = TbExperiment.objects.all()
    serializer_class = ExperimentDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'
