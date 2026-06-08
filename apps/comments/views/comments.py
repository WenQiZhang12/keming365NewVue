# -*- coding: utf-8 -*-
"""
apps.comments.views.comments - 评论相关视图

提供评论列表查看、发表、删除接口
"""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import TbUser
from apps.comments.models import TbItemComment
from apps.comments.serializers import CommentCreateSerializer, CommentSerializer
from utils.exceptions import BusinessError
from utils.pagination import StandardPagination

logger = logging.getLogger(__name__)


class CommentListView(APIView):
    """评论列表

    GET /api/v1/comments/?experiment_id=xxx
    匿名可访问
    """

    permission_classes = [AllowAny]

    def get(self, request):
        experiment_id = request.query_params.get('experiment_id')
        if not experiment_id:
            raise BusinessError(
                message='缺少 experiment_id 参数',
                code='MISSING_EXPERIMENT_ID',
                status_code=400,
            )

        queryset = TbItemComment.objects.filter(
            experimentId=experiment_id,
        ).order_by('-createTime')

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CommentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CommentCreateView(APIView):
    """发表评论

    POST /api/v1/comments/create/
    需要登录
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取当前用户
        user_id = request.user.id
        try:
            user = TbUser.objects.get(id=user_id)
        except TbUser.DoesNotExist:
            raise BusinessError(
                message='用户不存在',
                code='USER_NOT_FOUND',
                status_code=404,
            )

        # 构建评论对象
        comment = TbItemComment(
            id=serializer.validated_data['id'],
            userid=user_id,
            userNmae=user.name or user.username or '',
            experimentId=serializer.validated_data['experimentId'],
            commentContent=serializer.validated_data['content'],
            createTime=serializer.validated_data['createTime'],
            replyId=serializer.validated_data.get('replyId', None) or None,
            status=0,
        )
        comment.save()

        result_serializer = CommentSerializer(comment)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    """删除评论

    DELETE /api/v1/comments/<id>/
    需要登录
    - 只能删除自己的评论
    - 管理员可以删除任意评论
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # 查询评论
        try:
            comment = TbItemComment.objects.get(id=pk)
        except TbItemComment.DoesNotExist:
            raise BusinessError(
                message='评论不存在',
                code='COMMENT_NOT_FOUND',
                status_code=404,
            )

        user_id = request.user.id
        user_type = getattr(request.user, 'type', None)

        # 权限校验：仅评论所有者或管理员可删除
        is_owner = comment.userid == user_id
        is_admin = user_type == 2

        if not is_owner and not is_admin:
            raise BusinessError(
                message='没有权限删除此评论',
                code='PERMISSION_DENIED',
                status_code=403,
            )

        comment.delete()
        return Response(
            {'message': '评论删除成功'},
            status=status.HTTP_200_OK,
        )
