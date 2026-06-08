# -*- coding: utf-8 -*-
"""
apps.scores.views.scores - 成绩管理 视图

提供成绩查询、用时统计等接口。
"""

import logging

from django.db import connection
from django.db.models import Avg, Max, Min, Sum
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from django.utils.timezone import now

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import TbUser
from apps.scores.models import TbExperimentScore, TbExperimentUsetime
from apps.scores.serializers import ExperimentScoreSerializer, UsetimeSerializer
from utils.exceptions import BusinessError
from utils.pagination import StandardPagination

logger = logging.getLogger(__name__)


# ============================================================================
# 我的成绩
# ============================================================================

class MyScoreView(APIView, StandardPagination):
    """我的实验成绩列表

    GET /api/v1/scores/my/
    需要认证

    返回当前登录用户的实验成绩，按时间倒序排列，支持分页。

    查询参数:
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        # 查询当前用户的所有成绩，按时间倒序
        queryset = TbExperimentScore.objects.filter(
            userId=user_id,
        ).order_by('-createTime')

        # 分页
        page = self.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ExperimentScoreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 不分页（兜底）
        serializer = ExperimentScoreSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# 实验成绩详情
# ============================================================================

class ExperimentScoreDetailView(APIView):
    """实验成绩详情

    GET /api/v1/scores/experiment/<id>/
    需要认证

    返回指定实验的成绩详情：
      - 教师（type=1）和管理员（type=2）可以查看所有用户的成绩
      - 学生（type=0）只能查看自己的成绩

    URL 参数:
      id - 实验成绩记录 ID (TbExperimentScore.id)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user_id = request.user.id
        user_type = getattr(request.user, 'type', 0)

        try:
            score_obj = TbExperimentScore.objects.get(id=pk)
        except TbExperimentScore.DoesNotExist:
            raise BusinessError(
                message='成绩记录不存在',
                code='SCORE_NOT_FOUND',
                status_code=404,
            )

        # 权限校验：学生只能看自己的记录
        if user_type == 0 and score_obj.userId != user_id:
            raise BusinessError(
                message='无权查看其他用户的成绩',
                code='PERMISSION_DENIED',
                status_code=403,
            )

        serializer = ExperimentScoreSerializer(score_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# 实验用时统计
# ============================================================================

class UsetimeStatsView(APIView):
    """实验用时统计

    GET /api/v1/scores/time-stats/
    需要认证

    返回当前用户的实验用时统计，支持按时间范围过滤。

    查询参数:
      start_date - 开始日期（可选，格式：YYYY-MM-DD）
      end_date   - 结束日期（可选，格式：YYYY-MM-DD）
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        # 构建查询条件
        filters = {'userId': user_id}

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start is None:
                raise BusinessError(
                    message='start_date 格式无效，请使用 YYYY-MM-DD 格式',
                    code='INVALID_DATE_FORMAT',
                    status_code=400,
                )
            filters['createTime__gte'] = parsed_start

        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end is None:
                raise BusinessError(
                    message='end_date 格式无效，请使用 YYYY-MM-DD 格式',
                    code='INVALID_DATE_FORMAT',
                    status_code=400,
                )
            filters['createTime__lte'] = parsed_end

        # 查询用时数据
        queryset = TbExperimentUsetime.objects.filter(**filters)

        total_experiments = queryset.count()

        # 获取用时字段的值（usetime 是 CharField，需要转为 float）
        def safe_to_float(value, default=0.0):
            if value is None:
                return default
            try:
                return round(float(value), 2)
            except (ValueError, TypeError):
                return default

        total_time = sum(
            safe_to_float(item.usetime) for item in queryset
        )

        time_values = [
            safe_to_float(item.usetime)
            for item in queryset
            if item.usetime is not None
        ]

        avg_time = round(sum(time_values) / len(time_values), 2) if time_values else 0.0
        max_time = round(max(time_values), 2) if time_values else 0.0
        min_time = round(min(time_values), 2) if time_values else 0.0

        # 详细记录
        details_serializer = UsetimeSerializer(queryset.order_by('-createTime'), many=True)

        return Response({
            'totalExperiments': total_experiments,
            'totalTime': round(total_time, 2),
            'avgTime': avg_time,
            'maxTime': max_time,
            'minTime': min_time,
            'details': details_serializer.data,
        }, status=status.HTTP_200_OK)


# ============================================================================
# 我的实验（已练习过的实验列表）
# ============================================================================


def _get_experiment_title(experiment_id):
    """从 tb_experiment 获取实验名称"""
    from apps.courses.models import TbExperiment
    try:
        exp = TbExperiment.objects.only('title').get(id=experiment_id)
        return exp.title or ''
    except TbExperiment.DoesNotExist:
        return ''


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_experiments(request):
    """
    GET /api/v1/scores/my-experiments/
    获取当前用户已点击过[开始实验]的实验列表。
    数据来源：tb_experiment_record 表。
    """
    user_id = request.user.id

    with connection.cursor() as cur:
        cur.execute(
            "SELECT experiment_Id, record_num, MAX(create_time) as first_time FROM tb_experiment_record WHERE user_Id=%s GROUP BY experiment_Id ORDER BY first_time DESC",
            [user_id]
        )
        rows = cur.fetchall()

    results = []
    for row in rows:
        exp_id = row[0]
        title = _get_experiment_title(exp_id)
        results.append({
            'id': exp_id,
            'title': title or '未知实验',
            'practiceCount': row[1] or 0,
            'firstPracticeTime': str(row[2])[:19] if row[2] else '',
        })

    return Response({
        'count': len(results),
        'results': results,
    })
