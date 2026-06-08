# -*- coding: utf-8 -*-
"""
apps.quizzes.views.quizzes - 测验 视图

提供题目列表获取、答案提交等接口。
"""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Chapter, TbExperiment
from apps.quizzes.models import Question
from apps.quizzes.serializers import (
    AnswerResultSerializer,
    QuestionSerializer,
    QuestionSubmitSerializer,
)
from apps.scores.models import TbExperimentScore

logger = logging.getLogger(__name__)


def _parse_question_ids(question_list_str: str | None) -> list[int]:
    """将逗号分隔的题目 ID 字符串解析为 int 列表"""
    if not question_list_str:
        return []
    ids = []
    for part in question_list_str.split(','):
        part = part.strip()
        if part and part.isdigit():
            ids.append(int(part))
    return ids


def _get_questions_for_experiment(experiment_id: str) -> list[Question]:
    """根据 experiment_id 获取实验关联的所有题目

    关联方式：
      1. 通过 TbExperiment.chapterId 定位到 Chapter
      2. 从 Chapter.video_question_list 和 Chapter.question_list
         中解析出题目 ID 列表
    """
    try:
        experiment = TbExperiment.objects.get(pk=experiment_id)
    except TbExperiment.DoesNotExist:
        return []

    # 通过章节获取题目 ID
    try:
        chapter = Chapter.objects.get(pk=experiment.chapterId)
    except (Chapter.DoesNotExist, ValueError, TypeError):
        return []

    question_ids = set()
    question_ids.update(_parse_question_ids(chapter.videoQuestionList))
    question_ids.update(_parse_question_ids(chapter.questionList))

    if not question_ids:
        return []

    questions = Question.objects.filter(questionId__in=question_ids)
    return list(questions)


# ============================================================================
# 题目列表
# ============================================================================

class QuestionListView(APIView):
    """获取实验关联的题目列表

    GET /api/v1/quizzes/<experiment_id>/

    匿名可访问，每道题不返回答案（前端做题用）。
    题目来源于实验所在章节关联的 video_question_list 和 question_list。
    """

    permission_classes = [AllowAny]

    def get(self, request, experiment_id: str):
        questions = _get_questions_for_experiment(experiment_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response({
            'count': len(questions),
            'results': serializer.data,
        })


# ============================================================================
# 答案提交
# ============================================================================

class QuestionSubmitView(APIView):
    """提交实验测验答案

    POST /api/v1/quizzes/<experiment_id>/submit/

    需要登录。
    请求体：{ "answers": [{ "questionId": 1, "selectedAnswer": "A" }, ...] }
    返回每道题的对错结果。
    如果该实验有 TbExperimentScore 记录，自动更新 scoreSum。
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, experiment_id: str):
        serializer = QuestionSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answers = serializer.validated_data['answers']

        # 批量查询所有涉及的题目
        question_ids = [item['questionId'] for item in answers]
        questions_map = {
            q.questionId: q
            for q in Question.objects.filter(questionId__in=question_ids)
        }

        # 逐题对比答案
        results = []
        correct_count = 0
        for item in answers:
            qid = item['questionId']
            selected = item['selectedAnswer']
            question = questions_map.get(qid)

            if question is None:
                results.append({
                    'questionId': qid,
                    'questionTopic': None,
                    'selectedAnswer': selected,
                    'correctAnswer': '',
                    'isCorrect': False,
                    'questionExplain': None,
                })
                continue

            is_correct = (selected.strip().upper() == question.questionAnswer.strip().upper())
            if is_correct:
                correct_count += 1

            results.append({
                'questionId': qid,
                'questionTopic': question.questionTopic,
                'selectedAnswer': selected,
                'correctAnswer': question.questionAnswer,
                'isCorrect': is_correct,
                'questionExplain': question.questionExplain,
            })

        # 如果有 TbExperimentScore 记录，更新 scoreSum
        user = request.user
        self._update_score_if_exists(user, experiment_id, correct_count, len(results))

        result_serializer = AnswerResultSerializer(results, many=True)
        return Response({
            'total': len(results),
            'correctCount': correct_count,
            'results': result_serializer.data,
        })

    def _update_score_if_exists(self, user, experiment_id: str, correct: int, total: int):
        """尝试查找并更新实验成绩中的考试分数"""
        user_id = str(user.id) if hasattr(user, 'id') else ''

        if not user_id:
            return

        # 支持多种用户 ID 字段
        try:
            score_record = TbExperimentScore.objects.filter(
                experimentId=experiment_id,
            ).filter(
                # 匹配 userId 或 idCard 或 un
                user_id__in=[user_id, user.username or '', getattr(user, 'phone', '')]
            ).first()
        except Exception:
            logger.warning('查找 TbExperimentScore 失败', exc_info=True)
            return

        if score_record is None:
            return

        # 计算正确率作为考试分数（百分比换算为百分制）
        if total > 0:
            quiz_score = round((correct / total) * 100, 2)
        else:
            quiz_score = 0.0

        score_record.scoreSum = quiz_score
        score_record.save(update_fields=['scoreSum', 'updateTime'])
        logger.info(
            '已更新实验成绩: experiment=%s, user=%s, scoreSum=%s',
            experiment_id, user_id, quiz_score,
        )
