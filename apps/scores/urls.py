# -*- coding: utf-8 -*-
"""
apps.scores.urls - 成绩管理 路由

路由前缀（在 config/urls.py 中定义）：/api/v1/scores/
"""

from django.urls import path, re_path

from apps.scores.views.scores import (
    ExperimentScoreDetailView,
    MyScoreView,
    UsetimeStatsView,
    my_experiments,
)
from apps.scores.views.teacher_report import (
    teacher_class_list,
    teacher_course_list,
    teacher_experiment_list,
    teacher_report_list,
    teacher_report_detail,
    teacher_submit_score,
)
from apps.scores.views.student_report import student_report_list

app_name = 'scores'

urlpatterns = [
    # --- 实验成绩 ---
    path('my/', MyScoreView.as_view(), name='my_scores'),
    path('my-experiments/', my_experiments, name='my_experiments'),
    path('experiment/<str:pk>/', ExperimentScoreDetailView.as_view(), name='score_detail'),
    path('time-stats/', UsetimeStatsView.as_view(), name='time_stats'),
    # --- 教师实验报告管理 ---
    path('teacher/classes/', teacher_class_list, name='teacher_class_list'),
    path('teacher/courses/', teacher_course_list, name='teacher_course_list'),
    path('teacher/experiments/', teacher_experiment_list, name='teacher_experiment_list'),
    path('teacher/reports/', teacher_report_list, name='teacher_report_list'),
    re_path(r'^teacher/report/(?P<report_id>[^/]+)/$', teacher_report_detail, name='teacher_report_detail'),
    re_path(r'^teacher/report/(?P<report_id>[^/]+)/score/$', teacher_submit_score, name='teacher_submit_score'),
    # --- 学生实验报告 ---
    path('student/reports/', student_report_list, name='student_report_list'),
]
