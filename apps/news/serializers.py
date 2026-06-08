# -*- coding: utf-8 -*-
"""
apps.news.serializers - 新闻与公告 序列化器
"""

from rest_framework import serializers

from apps.news.models import News


class NewsSerializer(serializers.ModelSerializer):
    """
    新闻列表序列化器

    返回新闻的基本信息和摘要。
    content 仅返回前 200 字符作为摘要。
    """

    class Meta:
        model = News
        fields = [
            'id',
            'title',
            'content',
            'author',
            'coverImg',
            'type',
            'browsetimes',
            'priority',
            'createTime',
        ]

    author = serializers.IntegerField(source='userid', read_only=True)
    type = serializers.CharField(source='timeStr', read_only=True)
    createTime = serializers.DateTimeField(source='time', read_only=True)

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        """列表场景仅返回前 200 字符摘要"""
        if obj.content and len(obj.content) > 200:
            return obj.content[:200] + '...'
        return obj.content or ''


class NewsDetailSerializer(serializers.ModelSerializer):
    """
    新闻详情序列化器

    返回新闻全部字段，content 全文返回。
    """

    class Meta:
        model = News
        fields = '__all__'

    author = serializers.IntegerField(source='userid', read_only=True)
    type = serializers.CharField(source='timeStr', read_only=True)
    createTime = serializers.DateTimeField(source='time', read_only=True)
