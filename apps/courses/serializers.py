# -*- coding: utf-8 -*-
"""
apps.courses.serializers - 课程/章节/实验 序列化器
"""

from rest_framework import serializers

from apps.courses.models import (
    Chapter,
    Node,
    TbCurriculum,
    TbExperiment,
    TbExperimentReport,
    UserCurriculum,
)


# ============================================================================
# 课程列表
# ============================================================================

class CurriculumListSerializer(serializers.ModelSerializer):
    """课程列表序列化器"""

    experimentCount = serializers.SerializerMethodField(
        help_text='实验数量'
    )

    class Meta:
        model = TbCurriculum
        fields = [
            'id', 'curriculumName', 'price',
            'classifyId', 'status', 'createTime', 'sortOrder',
            'experimentCount',
        ]

    def get_experimentCount(self, obj):
        """统计该课程下的实验数量（通过 parentId 关联）"""
        from apps.courses.models import TbExperiment
        return TbExperiment.objects.filter(parentId=obj.id).count()


# ============================================================================
# 实验（列表 & 详情）
# ============================================================================

class ExperimentListSerializer(serializers.ModelSerializer):
    """实验列表序列化器"""

    image = serializers.SerializerMethodField()

    class Meta:
        model = TbExperiment
        fields = [
            'id', 'title', 'publisher', 'image',
            'price', 'sellPoint', 'type', 'status',
            'appliId',
            'createTime', 'chapterId', 'nodeId',
        ]

    def get_image(self, obj):
        """如果实验没有图片，返回课程的图片"""
        if obj.image:
            return obj.image
        # 通过 parentId 查找课程图片
        try:
            curriculum = TbCurriculum.objects.filter(id=obj.parentId).first()
            if curriculum and curriculum.image:
                return curriculum.image
        except Exception:
            pass
        return ''


class ExperimentDetailSerializer(serializers.ModelSerializer):
    """实验详情序列化器"""

    class Meta:
        model = TbExperiment
        fields = '__all__'


class ExperimentReportSerializer(serializers.ModelSerializer):
    """实验报告序列化器"""

    class Meta:
        model = TbExperimentReport
        fields = [
            'id', 'fileName', 'type',
            'userId', 'experimentId', 'reportScore', 'createTime',
        ]


# ============================================================================
# 章节树
# ============================================================================

class NodeTreeSerializer(serializers.ModelSerializer):
    """知识节点（章节树子级）序列化器"""

    class Meta:
        model = Node
        fields = [
            'id', 'title', 'order',
            'pptpath', 'createTime',
        ]


class ChapterTreeSerializer(serializers.ModelSerializer):
    """章节树序列化器（递归嵌套 Node）"""

    node = serializers.SerializerMethodField(help_text='子级知识节点')

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'type', 'order',
            'pdfPath', 'createTime', 'node',
        ]

    def get_node(self, obj):
        """获取章节下的知识节点，按 order 排序"""
        nodes = Node.objects.filter(chapterId=obj.id).order_by('order')
        return NodeTreeSerializer(nodes, many=True).data


# ============================================================================
# 课程详情
# ============================================================================

class CurriculumDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器"""

    experiments = serializers.SerializerMethodField(
        help_text='该课程下的实验列表'
    )
    chapters = serializers.SerializerMethodField(
        help_text='章节树'
    )

    class Meta:
        model = TbCurriculum
        fields = [
            'id', 'classifyId', 'status', 'curriculumName', 'createTime',
            'updateTime', 'sortOrder', 'price', 'experiments', 'chapters',
        ]

    def get_experiments(self, obj):
        """获取课程下的实验列表"""
        # 优先通过 parentId 关联课程
        experiments = TbExperiment.objects.filter(
            parentId=obj.id
        ).order_by('-createTime')
        return ExperimentListSerializer(experiments, many=True).data

    def get_chapters(self, obj):
        """获取课程下的章节树，按 order 排序"""
        chapters = Chapter.objects.filter(
            curriculumId=obj.id
        ).order_by('order')
        return ChapterTreeSerializer(chapters, many=True).data


# ============================================================================
# 学习计划
# ============================================================================

class StudyPlanCurriculumSerializer(serializers.ModelSerializer):
    """学习计划中嵌套的课程信息"""

    class Meta:
        model = TbCurriculum
        fields = [
            'id', 'curriculumName', 'price',
            'classifyId', 'status',
        ]


class StudyPlanSerializer(serializers.ModelSerializer):
    """学习计划序列化器（UserCurriculum）"""

    curriculum = serializers.SerializerMethodField(
        help_text='课程信息'
    )

    class Meta:
        model = UserCurriculum
        fields = [
            'id', 'userId', 'curriculumId', 'flag',
            'createTime', 'expirationTime', 'curriculum',
        ]

    def get_curriculum(self, obj):
        """获取关联的课程信息"""
        try:
            curriculum = TbCurriculum.objects.get(id=obj.curriculumId)
            return StudyPlanCurriculumSerializer(curriculum).data
        except TbCurriculum.DoesNotExist:
            return None
