# -*- coding: utf-8 -*-
"""
apps.comments.serializers - 评论与讨论 序列化器
"""

from rest_framework import serializers

from apps.accounts.models import TbUser
from apps.comments.models import TbItemComment


class UserBriefSerializer(serializers.Serializer):
    """用户简要信息序列化器（嵌套在评论中使用）"""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    userImg = serializers.CharField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器（只读，用于列表/详情返回）"""

    id = serializers.CharField(read_only=True)
    userId = serializers.CharField(source='userid', read_only=True)
    userName = serializers.CharField(source='userNmae', read_only=True)
    content = serializers.CharField(source='commentContent', read_only=True)
    createTime = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    replyId = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(help_text='用户信息（嵌套）')

    class Meta:
        model = TbItemComment
        fields = [
            'id', 'userId', 'userName', 'content', 'createTime', 'replyId', 'user',
        ]

    def get_user(self, obj):
        """根据 userId（userid 字段）查询用户简要信息"""
        if not obj.userid:
            return None
        try:
            user = TbUser.objects.get(id=obj.userid)
            return UserBriefSerializer(user).data
        except TbUser.DoesNotExist:
            return None


class CommentCreateSerializer(serializers.Serializer):
    """发表评论序列化器（输入）"""

    experimentId = serializers.CharField(
        max_length=255, required=True, help_text='实验 ID',
    )
    content = serializers.CharField(
        max_length=255, required=True, help_text='评论内容',
    )
    replyId = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True,
        help_text='回复的评论 ID（可选）',
    )

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('评论内容不能为空')
        return value.strip()

    def validate(self, attrs):
        import uuid
        from django.utils import timezone
        attrs['id'] = str(uuid.uuid4()).replace('-', '')[:32]
        attrs['createTime'] = timezone.now()
        return attrs
