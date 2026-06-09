# -*- coding: utf-8 -*-
"apps.courses.urls - 课程管理 路由"

from django.urls import path

from apps.courses.views import (
    ChapterDetailView,
    ChapterTreeView,
    CurriculumDetailView,
    CurriculumListView,
    ExperimentDetailView,
    ExperimentListView,
    StudyPlanCreateView,
    StudyPlanListView,
)
from apps.courses.views.statistics import (
    experiment_record_info,
    experiment_stats,
    record_practice,
    record_visit,
)
from apps.courses.views.yqcloud import YQPathView
from apps.home.views.home import ClassifyListView

urlpatterns = [
    # 学科分类
    path('classifies/', ClassifyListView.as_view(), name='classify_list'),
    # 课程
    path('experiments/', ExperimentListView.as_view(), name='experiment_list'),
    path('experiments/<str:pk>/', ExperimentDetailView.as_view(), name='experiment_detail'),
    path('experiments/<str:pk>/yqpath/', YQPathView.as_view(), name='experiment_yqpath'),
    path('experiments/<str:pk>/stats/', experiment_stats, name='experiment_stats'),
    path('experiments/<str:pk>/record-visit/', record_visit, name='record_visit'),
    path('experiments/<str:pk>/record-practice/', record_practice, name='record_practice'),
    # 兼容旧Java接口
    path('record/experimentRecordInfo', experiment_record_info, name='experiment_record_info'),
    path('chapters/<int:pk>/', ChapterDetailView.as_view(), name='chapter_detail'),
    # 学习计划
    path('study-plans/', StudyPlanListView.as_view(), name='study_plan_list'),
    path('study-plans/add/', StudyPlanCreateView.as_view(), name='study_plan_add'),
    path('', CurriculumListView.as_view(), name='course_list'),
    path('<str:pk>/', CurriculumDetailView.as_view(), name='course_detail'),
    # 章节
    path('<str:curriculum_id>/chapters/', ChapterTreeView.as_view(), name='chapter_tree'),
]
