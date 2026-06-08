# -*- coding: utf-8 -*-
"apps.quizzes.urls - 测验与考试 路由"

from django.urls import path

from apps.quizzes.views.quizzes import QuestionListView, QuestionSubmitView

urlpatterns = [
    path('<str:experiment_id>/', QuestionListView.as_view(), name='quiz_questions'),
    path('<str:experiment_id>/submit/', QuestionSubmitView.as_view(), name='quiz_submit'),
]
