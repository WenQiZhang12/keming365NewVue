# -*- coding: utf-8 -*-
"""
Assessment App - 路由
对应 Java AssessmentController 所有接口
"""

from django.urls import path

from apps.assessment.views import (
    visit_page,
    visit_manage,
    auth_member,
    member_info,
    class_info,
    course_info,
    section_info,
    course_index,
    section_index,
    class_index,
    major_index,
    major_info,
)
from apps.assessment.batch_score import batch_update_score
from apps.assessment.pushlet import get_pull_event, get_experiment_pushlet
from apps.assessment.show_ppt import show_ppt, show_ppt_by_qrcode, scan_qrcode
from apps.assessment.export_excel import export_score

urlpatterns = [
    # 进入考试
    path('visit-page/', visit_page, name='assess_visit_page'),
    # 考试管理
    path('visit-manage/', visit_manage, name='assess_visit_manage'),
    # 验证用户
    path('auth-member/', auth_member, name='assess_auth_member'),
    # 用户信息
    path('member-info/', member_info, name='assess_member_info'),
    # 班级信息
    path('class-info/', class_info, name='assess_class_info'),
    # 课程信息
    path('course-info/', course_info, name='assess_course_info'),
    # 实验信息
    path('section-info/', section_info, name='assess_section_info'),
    # 班级下所有课程
    path('course-index/', course_index, name='assess_course_index'),
    # 课程下所有实验
    path('section-index/', section_index, name='assess_section_index'),
    # 用户所有班级
    path('class-index/', class_index, name='assess_class_index'),
    # 分类列表
    path('major-index/', major_index, name='assess_major_index'),
    # 分类信息
    path('major-info/', major_info, name='assess_major_info'),
    # 批量更新总分
    path('batch/update-score/', batch_update_score, name='assess_batch_update_score'),
    # 推送/云雀实验进入
    path('pushlet/pull-event/', get_pull_event, name='assess_pull_event'),
    path('pushlet/experiment-pushlet/', get_experiment_pushlet, name='assess_experiment_pushlet'),
    # PPT/VR 资源展示
    path('show-ppt/', show_ppt, name='assess_show_ppt'),
    path('show-ppt/qrcode/', show_ppt_by_qrcode, name='assess_show_ppt_qrcode'),
    path('show-ppt/scan-qrcode/', scan_qrcode, name='assess_scan_qrcode'),
    # Excel 导出
    path('export/score/', export_score, name='assess_export_score'),
]
