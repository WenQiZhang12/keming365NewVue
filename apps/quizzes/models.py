# -*- coding: utf-8 -*-
"""
Quizzes App Models
从 Java POJO 逆向生成，对应原 Java 实体类
"""

from django.db import models

class Question(models.Model):
    """
    Question - 对应 Java POJO: com.km.jxpt.pojo.Question
    原表名: question
    """
    questionId = models.IntegerField(null=True, blank=True, db_column='question_id')
    questionTopic = models.CharField(max_length=255, null=True, blank=True, db_column='question_topic')
    questionA = models.CharField(max_length=255, null=True, blank=True, db_column='question_a')
    questionB = models.CharField(max_length=255, null=True, blank=True, db_column='question_b')
    questionC = models.CharField(max_length=255, null=True, blank=True, db_column='question_c')
    questionD = models.CharField(max_length=255, null=True, blank=True, db_column='question_d')
    questionE = models.CharField(max_length=255, null=True, blank=True, db_column='question_e')
    questionF = models.CharField(max_length=255, null=True, blank=True, db_column='question_f')
    questionG = models.CharField(max_length=255, null=True, blank=True, db_column='question_g')
    questionAnswer = models.CharField(max_length=255, null=True, blank=True, db_column='question_answer')
    questionExplain = models.CharField(max_length=255, null=True, blank=True, db_column='question_explain')
    questionImage = models.CharField(max_length=255, null=True, blank=True, db_column='question_image')
    parentId = models.IntegerField(null=True, blank=True, db_column='parent_id')
    videoId = models.IntegerField(null=True, blank=True, db_column='video_id')
    questionError = models.IntegerField(null=True, blank=True, db_column='question_error')
    questionType = models.IntegerField(null=True, blank=True, db_column='question_type')
    questionTest = models.CharField(max_length=255, null=True, blank=True, db_column='question_test')
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    deleted = models.IntegerField(null=True, blank=True)
    timestamp = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'question'

    def __str__(self):
        return str(self.id)
