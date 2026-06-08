# -*- coding: utf-8 -*-
"apps.comments.urls - 评论与讨论 路由"

from django.urls import path

from apps.comments.views import (
    CommentCreateView,
    CommentDeleteView,
    CommentListView,
)

urlpatterns = [
    path('', CommentListView.as_view(), name='comment_list'),
    path('create/', CommentCreateView.as_view(), name='comment_create'),
    path('<str:pk>/', CommentDeleteView.as_view(), name='comment_delete'),
]
