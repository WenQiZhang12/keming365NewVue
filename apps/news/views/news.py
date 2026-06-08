# -*- coding: utf-8 -*-
"""
apps.news.views.news - 新闻与公告 视图

所有新闻接口允许匿名访问。
"""

from django.db.models import F
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.news.models import News
from apps.news.serializers import NewsDetailSerializer, NewsSerializer
from utils.pagination import StandardPagination


class NewsListView(ListAPIView):
    """
    GET /api/v1/news/

    新闻列表（分页）。

    按 priority 降序、createTime 降序排列。
    支持通过 type 参数过滤（对应 timeStr 字段）。

    查询参数：
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
      type      - 新闻类型过滤（可选，对应 timeStr 字段）
    """

    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        # type 过滤（对应 timeStr 字段）
        news_type = self.request.query_params.get('type')
        if news_type:
            qs = qs.filter(timeStr=news_type)
        # search 搜索标题
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.order_by('-priority', '-time')


class NewsDetailView(RetrieveAPIView):
    """
    GET /api/v1/news/<id>/

    新闻详情。

    每次访问自动将 browsetimes +1。
    """

    queryset = News.objects.all()
    serializer_class = NewsDetailSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 访问量 +1
        News.objects.filter(pk=instance.pk).update(
            browsetimes=F('browsetimes') + 1,
        )
        # 刷新实例以获取最新值
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
