# -*- coding: utf-8 -*-
"""
apps.courses.views.study_plan - 学习计划 视图

学习计划接口需要登录。
"""

from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.courses.models import UserCurriculum
from apps.courses.serializers import StudyPlanSerializer
from utils.pagination import StandardPagination


class StudyPlanListView(ListAPIView):
    """
    GET /api/v1/study-plans/

    查看我购买/关联的课程列表（需登录）

    查询参数：
      page      - 页码（默认 1）
      page_size - 每页数量（默认 20，最大 100）
    """
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        user_id = self.request.user.id
        return UserCurriculum.objects.filter(
            userId=user_id
        ).order_by('-createTime')


class StudyPlanCreateView(CreateAPIView):
    """
    POST /api/v1/study-plans/add/

    添加课程到学习计划（需登录）

    请求体：
      curriculumId - 课程 ID（必填）
    """
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        curriculum_id = request.data.get('curriculumId')
        user_id = request.user.id

        if not curriculum_id:
            return Response(
                {'detail': '课程 ID 不能为空'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查是否已存在
        existing = UserCurriculum.objects.filter(
            userId=user_id,
            curriculumId=curriculum_id,
        ).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 创建学习计划记录
        from django.utils import timezone
        import uuid

        instance = UserCurriculum.objects.create(
            id=str(uuid.uuid4()).replace('-', '')[:32],
            userId=user_id,
            curriculumId=curriculum_id,
            flag=1,
            createTime=timezone.now(),
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
