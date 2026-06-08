# -*- coding: utf-8 -*-
"""
apps.courses.views.yqcloud - 云渲染路径获取接口
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import TbExperiment
from apps.courses.yqcloud import get_yq_path_from_experiment
from utils.permissions import IsAdminUser

logger = logging.getLogger(__name__)


class YQPathView(APIView):
    """
    POST /api/v1/courses/experiments/<id>/yqpath/

    获取云渲染实验路径

    前端调用时机：
        用户点击"开始实验"按钮时调用此接口

    请求参数（URL path）：
        id - 实验 ID

    返回：
        {
            "code": 0,
            "resultUrl": "https://...",  # Unity 实验 URL
            "token": "...",
            "timestamp": 1234567890,
            "msg": "success"
        }

    错误码：
        0  - 成功
        1  - 参数错误
        2  - 云平台错误
        401 - 未登录
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # 获取实验
        try:
            experiment = TbExperiment.objects.get(pk=pk)
        except TbExperiment.DoesNotExist:
            return Response({
                'code': 1,
                'message': '实验不存在',
                'details': {},
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查实验状态（开发阶段跳过）
        # if str(experiment.status) != '1':
        #     return Response({
        #         'code': 1,
        #         'message': '实验已下架',
        #         'details': {},
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # 调用云渲染接口
        result = get_yq_path_from_experiment(experiment, request.user, request)

        if result['code'] != 0:
            return Response({
                'code': result['code'],
                'message': result['msg'],
                'details': {},
            }, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'code': 0,
            'message': 'success',
            'details': {
                'resultUrl': result['resultUrl'],
                'token': result['token'],
                'timestamp': result['timestamp'],
            },
        })
