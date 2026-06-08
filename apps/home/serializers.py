# -*- coding: utf-8 -*-
"""
apps.home.serializers - 首页 序列化器
"""

from rest_framework import serializers

from apps.common.models import TbClassify
from apps.courses.models import TbExperiment, TbCurriculum
from apps.home.models import TbViewpager, TbHot, TbIntro, TbItemCat


# ─────────────────────────────────────────────────────────────
# 学科分类
# ─────────────────────────────────────────────────────────────

class ClassifySerializer(serializers.ModelSerializer):
    """学科分类序列化"""
    className = serializers.SerializerMethodField()
    sortOrder = serializers.IntegerField(source='sort_order', read_only=True)

    class Meta:
        model = TbClassify
        fields = ['id', 'className', 'sortOrder', 'status']

    def get_className(self, obj):
        """Fix double-encoded Chinese text"""
        raw = getattr(obj, 'class_name', None) or getattr(obj, 'className', None)
        if not raw:
            return raw
        try:
            # Try iso-8859-1 -> utf-8 fix for double-encoded data
            fixed = raw.encode('iso-8859-1').decode('utf-8')
            return fixed
        except:
            return raw


# ─────────────────────────────────────────────────────────────
# 轮播图
# ─────────────────────────────────────────────────────────────

class ViewpagerSerializer(serializers.ModelSerializer):
    """轮播图序列化"""
    image = serializers.CharField(source='imgPath', read_only=True)
    url = serializers.CharField(source='imgPath', read_only=True)
    status = serializers.IntegerField(source='flag', read_only=True)

    class Meta:
        model = TbViewpager
        fields = ['id', 'title', 'image', 'url', 'sortOrder', 'status']


# ─────────────────────────────────────────────────────────────
# 栏目分类（含递归子项）
# ─────────────────────────────────────────────────────────────

class ItemCategorySerializer(serializers.ModelSerializer):
    """栏目分类序列化（含递归子项）"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = TbItemCat
        fields = ['id', 'name', 'parentId', 'sortOrder', 'children']

    def get_children(self, obj):
        """递归获取子分类（仅 active 状态）"""
        children = TbItemCat.objects.filter(
            parentId=obj.id,
            status=1,
            isParent=0,  # 叶子节点
        ).order_by('sortOrder')
        if children.exists():
            return ItemCategorySerializer(children, many=True).data
        return []


# ─────────────────────────────────────────────────────────────
# 热搜词
# ─────────────────────────────────────────────────────────────

class HotSearchSerializer(serializers.ModelSerializer):
    """热搜词序列化"""
    name = serializers.CharField(source='ename', read_only=True)
    count = serializers.SerializerMethodField()

    class Meta:
        model = TbHot
        fields = ['id', 'name', 'count']

    def get_count(self, obj):
        return obj.sortOrder or 0


# ─────────────────────────────────────────────────────────────
# 平台简介
# ─────────────────────────────────────────────────────────────

class IntroSerializer(serializers.ModelSerializer):
    """平台简介序列化"""
    image = serializers.CharField(read_only=True, default='')
    createTime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TbIntro
        fields = ['id', 'title', 'content', 'image', 'createTime']


# ─────────────────────────────────────────────────────────────
# 搜索专用序列化（搜索结果统一结构）
# ─────────────────────────────────────────────────────────────

class SearchExperimentSerializer(serializers.ModelSerializer):
    """实验搜索结果序列化"""
    type = serializers.SerializerMethodField()

    class Meta:
        model = TbExperiment
        fields = ['id', 'title', 'publisher', 'price', 'image',
                   'sellPoint', 'type', 'createTime']

    def get_type(self, obj):
        return 'experiment'


class SearchCurriculumSerializer(serializers.ModelSerializer):
    """课程搜索结果序列化"""
    type = serializers.SerializerMethodField()

    class Meta:
        model = TbCurriculum
        fields = ['id', 'curriculumName', 'price', 'type',
                   'createTime']

    def get_type(self, obj):
        return 'curriculum'
