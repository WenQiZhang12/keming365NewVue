# -*- coding: utf-8 -*-
"""
apps.quizzes.serializers - 测验与考试 序列化器

提供题目列表、答案提交等序列化。
"""

from rest_framework import serializers

from apps.quizzes.models import Question


# ============================================================================
# 题目序列化（列表/详情，不返回答案）
# ============================================================================

class QuestionSerializer(serializers.ModelSerializer):
    """题目序列化器

    用于前端做题时展示题目内容，不返回 questionAnswer 字段。
    is_correct 为只读字段，在提交答案后用于标记对错。
    """

    is_correct = serializers.BooleanField(read_only=True, default=None)

    class Meta:
        model = Question
        fields = [
            'questionId', 'questionTopic',
            'questionA', 'questionB', 'questionC', 'questionD',
            'questionE', 'questionF', 'questionG',
            'questionExplain', 'questionImage',
            'videoId', 'parentId', 'questionType', 'questionTest',
            'is_correct',
        ]


# ============================================================================
# 答案提交输入
# ============================================================================

class AnswerItemSerializer(serializers.Serializer):
    """单题答案提交输入"""

    questionId = serializers.IntegerField(help_text='题目 ID')
    selectedAnswer = serializers.CharField(
        max_length=255, help_text='用户选择的答案', allow_blank=True,
    )


class QuestionSubmitSerializer(serializers.Serializer):
    """提交答案序列化器

    输入：
      answers: [{questionId, selectedAnswer}, ...]

    输出（每道题）：
      questionId, questionTopic, selectedAnswer, correctAnswer,
      isCorrect, questionExplain
    """

    answers = AnswerItemSerializer(many=True, help_text='答案列表')


# ============================================================================
# 单题答案结果
# ============================================================================

class AnswerResultSerializer(serializers.Serializer):
    """单题答案结果序列化器"""

    questionId = serializers.IntegerField(help_text='题目 ID')
    questionTopic = serializers.CharField(
        max_length=255, help_text='题目内容', allow_null=True,
    )
    selectedAnswer = serializers.CharField(
        max_length=255, help_text='用户选择的答案',
    )
    correctAnswer = serializers.CharField(
        max_length=255, help_text='正确答案',
    )
    isCorrect = serializers.BooleanField(help_text='是否正确')
    questionExplain = serializers.CharField(
        max_length=255, help_text='题目解析', allow_null=True,
    )
