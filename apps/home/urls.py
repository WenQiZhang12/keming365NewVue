# -*- coding: utf-8 -*-
"apps.home.urls - 首页 路由"

from django.urls import path

from apps.home.views import (
    ClassifyListView,
    HotSearchListView,
    IntroView,
    ItemCategoryTreeView,
    SearchView,
    ViewpagerListView,
)

urlpatterns = [
    path('classify/', ClassifyListView.as_view(), name='classify_list'),
    path('viewpager/', ViewpagerListView.as_view(), name='viewpager_list'),
    path('categories/', ItemCategoryTreeView.as_view(), name='category_tree'),
    path('hot-search/', HotSearchListView.as_view(), name='hot_search'),
    path('search/', SearchView.as_view(), name='search'),
    path('intro/', IntroView.as_view(), name='intro'),
]
