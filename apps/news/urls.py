# -*- coding: utf-8 -*-
"""
apps.news.urls - 新闻与公告 路由

路由前缀：/api/v1/news/
"""

from django.urls import path

from apps.news.views.news import NewsDetailView, NewsListView

urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
]
