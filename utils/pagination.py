# -*- coding: utf-8 -*-
"""
utils.pagination - 通用分页类

提供标准分页功能，返回统一格式：
  {
    "count": 总记录数,
    "next": 下一页链接,
    "previous": 上一页链接,
    "results": 数据列表
  }

客户端通过 query 参数控制分页：
  ?page=1&page_size=20
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    标准分页

    支持参数：
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """

    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_size = 20

    def get_paginated_response(self, data):
        """统一的分页响应格式"""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })


class LargePagination(StandardPagination):
    """
    大分页 - 用于批量导出等场景

    默认每页 100，最大 500
    """

    page_size = 100
    max_page_size = 500
