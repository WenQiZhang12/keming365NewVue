# -*- coding: utf-8 -*-
"""
apps.home.views - 首页 视图

所有首页接口允许匿名访问。
"""

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import TbClassify
from apps.courses.models import TbExperiment, TbCurriculum
from apps.home.models import TbViewpager, TbHot, TbIntro, TbItemCat
from apps.home.serializers import (
    ClassifySerializer,
    HotSearchSerializer,
    IntroSerializer,
    ItemCategorySerializer,
    SearchCurriculumSerializer,
    SearchExperimentSerializer,
    ViewpagerSerializer,
)
from utils.pagination import StandardPagination


class ClassifyListView(ListAPIView):
    """
    GET /api/v1/home/classify/

    获取所有学科分类（按 sortOrder 排序）
    """
    queryset = TbClassify.objects.all().order_by('sortOrder')
    serializer_class = ClassifySerializer
    permission_classes = [AllowAny]


class ViewpagerListView(ListAPIView):
    """
    GET /api/v1/home/viewpager/

    获取所有轮播图列表（按 sortOrder 排序）
    """
    queryset = TbViewpager.objects.all().order_by('sortOrder')
    serializer_class = ViewpagerSerializer
    permission_classes = [AllowAny]


class ItemCategoryTreeView(ListAPIView):
    """
    GET /api/v1/home/categories/

    获取栏目分类树（仅返回顶级分类，含递归子项）
    """
    serializer_class = ItemCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return TbItemCat.objects.filter(
            parentId='0',  # 顶级分类
            isParent=1,
        ).order_by('sortOrder')


class HotSearchListView(ListAPIView):
    """
    GET /api/v1/home/hot-search/

    获取热搜词列表（按 sortOrder 排序）
    """
    queryset = TbHot.objects.all().order_by('sortOrder')
    serializer_class = HotSearchSerializer
    permission_classes = [AllowAny]


class SearchView(APIView):
    """
    GET /api/v1/home/search/

    搜索实验 / 课程

    查询参数：
      q         - 关键词（必填）
      type      - 搜索类型：experiment / curriculum，默认全部
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', '').strip().lower()

        if not q:
            return Response(
                {'detail': '请输入搜索关键词'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []

        # 搜索实验
        if not search_type or search_type == 'experiment':
            experiment_qs = TbExperiment.objects.filter(
                Q(title__icontains=q)
            ).order_by('-createTime')
            paginated_experiments = self.paginate_queryset(experiment_qs)
            if paginated_experiments is not None:
                exp_serializer = SearchExperimentSerializer(
                    paginated_experiments, many=True
                )
                results.extend(exp_serializer.data)
            else:
                # 未分页（全部返回）
                exp_serializer = SearchExperimentSerializer(
                    experiment_qs, many=True
                )
                results.extend(exp_serializer.data)

        # 搜索课程
        if not search_type or search_type == 'curriculum':
            curriculum_qs = TbCurriculum.objects.filter(
                Q(curriculumName__icontains=q)
            ).order_by('-createTime')
            paginated_curriculums = self.paginate_queryset(curriculum_qs)
            if paginated_curriculums is not None:
                cur_serializer = SearchCurriculumSerializer(
                    paginated_curriculums, many=True
                )
                results.extend(cur_serializer.data)
            else:
                cur_serializer = SearchCurriculumSerializer(
                    curriculum_qs, many=True
                )
                results.extend(cur_serializer.data)

        # 按创建时间统一排序（所有结果按时间降序）
        results.sort(key=lambda x: x.get('createTime') or '', reverse=True)

        return self.get_paginated_response(results)


class IntroView(ListAPIView):
    """
    GET /api/v1/home/intro/

    获取平台简介
    """
    queryset = TbIntro.objects.all()
    serializer_class = IntroSerializer
    permission_classes = [AllowAny]
