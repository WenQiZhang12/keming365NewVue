# -*- coding: utf-8 -*-
"""
apps.scores.serializers - 成绩管理 序列化器

提供实验成绩、实验记录、实验用时、个人总成绩等序列化器。
"""

from rest_framework import serializers

from apps.courses.models import TbExperiment
from apps.scores.models import (
    TbExperimentRecord,
    TbExperimentScore,
    TbExperimentUsetime,
    TbPersonScore,
)


# ============================================================================
# 实验成绩
# ============================================================================

class ExperimentScoreSerializer(serializers.ModelSerializer):
    """实验成绩序列化器

    字段：id, userId, experimentId, score, totalScore, usedTime, createTime, updateTime
    嵌套返回实验名称（experimentName）。
    """

    experimentName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TbExperimentScore
        fields = [
            'id',
            'userId',
            'experimentId',
            'score',       # 映射 scoreSum（总分）
            'totalScore',  # 映射 operationScore（操作分）
            'usedTime',    # 映射 useTime（用时）
            'experimentName',
            'createTime',
            'updateTime',
        ]

    def get_experimentName(self, obj) -> str:
        """从实验表或已存储的 experimentStr 获取实验名称"""
        # 优先返回数据库中已存储的名称
        if obj.experimentStr:
            return obj.experimentStr
        # 尝试从实验表中查询
        try:
            experiment = TbExperiment.objects.get(id=obj.experimentId)
            return experiment.title or ''
        except TbExperiment.DoesNotExist:
            return ''

    def to_representation(self, instance):
        """映射字段：将模型字段映射为接口所需的字段名"""
        ret = super().to_representation(instance)
        # 数据源字段映射
        ret['score'] = instance.scoreSum           # 总分 → score
        ret['totalScore'] = instance.operationScore  # 操作分 → totalScore
        ret['usedTime'] = instance.useTime           # 用时 → usedTime
        return ret


# ============================================================================
# 实验操作记录
# ============================================================================

class ExperimentRecordSerializer(serializers.ModelSerializer):
    """实验操作记录序列化器

    字段：id, userId, experimentId, score, recordData, createTime
    note: recordData 在原表中为 browseNum / recordNum 的 JSON 数据 (预留),
          当前返回空对象以保持接口兼容。
    """

    score = serializers.SerializerMethodField(read_only=True)
    recordData = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TbExperimentRecord
        fields = [
            'id',
            'userId',
            'experimentId',
            'score',
            'recordData',
            'createTime',
        ]

    def get_score(self, obj) -> float:
        """返回浏览/操作评分（暂无数据源，返回 0）"""
        return 0.0

    def get_recordData(self, obj) -> dict:
        """返回操作记录数据（预留字段，返回空对象）"""
        return {}


# ============================================================================
# 实验用时
# ============================================================================

class UsetimeSerializer(serializers.ModelSerializer):
    """实验用时序列化器

    字段：id, userId, experimentId, useTime, createTime
    """

    experimentName = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TbExperimentUsetime
        fields = [
            'id',
            'userId',
            'experimentId',
            'useTime',
            'experimentName',
            'createTime',
        ]

    def get_experimentName(self, obj) -> str:
        """获取实验名称"""
        if obj.ename:
            return obj.ename
        try:
            experiment = TbExperiment.objects.get(id=obj.eid)
            return experiment.title or ''
        except TbExperiment.DoesNotExist:
            return ''

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 数据源字段映射
        ret['useTime'] = instance.usetime     # usetime → useTime
        ret['experimentId'] = instance.eid     # eid → experimentId
        return ret


# ============================================================================
# 个人总成绩
# ============================================================================

class PersonScoreSerializer(serializers.ModelSerializer):
    """个人总成绩序列化器

    字段：id, userId, totalScore, experimentCount, createTime
    """

    totalScore = serializers.SerializerMethodField(read_only=True)
    experimentCount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TbPersonScore
        fields = [
            'id',
            'userId',
            'totalScore',
            'experimentCount',
            'createTime',
        ]

    def get_totalScore(self, obj) -> str:
        """返回 score 作为 totalScore"""
        return str(obj.score) if obj.score is not None else '0.00'

    def get_experimentCount(self, obj) -> int:
        """返回实验数量（暂无直接字段，默认 0）"""
        # 可通过搜索该用户所有成绩记录获得，但这里返回 0 以保持简单
        return 0


# ============================================================================
# 用时统计
# ============================================================================

class UsetimeStatsSerializer(serializers.Serializer):
    """用时统计序列化器（非 Model 绑定，用于响应格式化）"""

    totalExperiments = serializers.IntegerField(read_only=True, help_text='实验总数')
    totalTime = serializers.FloatField(read_only=True, help_text='总用时（秒）')
    avgTime = serializers.FloatField(read_only=True, help_text='平均用时（秒）')
    maxTime = serializers.FloatField(read_only=True, help_text='最长用时（秒）')
    minTime = serializers.FloatField(read_only=True, help_text='最短用时（秒）')
    details = serializers.ListField(read_only=True, help_text='详细记录')
